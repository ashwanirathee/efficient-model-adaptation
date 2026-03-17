import asyncio
import logging
import os
import queue
import sys
import tempfile
import threading
import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from dotenv import load_dotenv
from livekit.agents import cli
from mlx_audio.stt.utils import load_model as load_stt
from mlx_audio.tts.utils import load_model as load_tts
import requests
import re

load_dotenv(".env.local")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent")

MLX_LOCK = asyncio.Lock()

LOCAL_STT_ID="mlx-community/parakeet-tdt-0.6b-v3"
LOCAL_TTS_ID="mlx-community/Kokoro-82M-bf16"
LOCAL_TTS_VOICE="af_heart"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

class VoiceAssistant:
    def __init__(self, args=None):
        self.args = args
        self.local_stt = load_stt(os.getenv("LOCAL_STT_ID", LOCAL_STT_ID))
        self.local_tts = load_tts(os.getenv("LOCAL_TTS_ID", LOCAL_TTS_ID))

        if self.args is not None and self.args.utilize_remote:
            from ollama import Client
            self.ollama_client = Client(
                host="https://ollama.com",
                headers={'Authorization': 'Bearer ' + os.environ.get('OLLAMA_API_KEY')}
            )

    def record_until_stop(self, sample_rate: int = 16000, channels: int = 1) -> np.ndarray:
        q: queue.Queue[np.ndarray] = queue.Queue()
        stop_event = threading.Event()
        chunks: list[np.ndarray] = []

        def callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(indata.copy())

        def wait_for_stop():
            while True:
                cmd = input().strip()
                if cmd == "2":
                    stop_event.set()
                    break

        print("Recording... press 2 then Enter to stop.")
        threading.Thread(target=wait_for_stop, daemon=True).start()

        with sd.InputStream(
            samplerate=sample_rate,
            channels=channels,
            dtype="int16",
            callback=callback,
            blocksize=1024,
        ):
            while not stop_event.is_set():
                try:
                    chunk = q.get(timeout=0.1)
                    chunks.append(chunk)
                except queue.Empty:
                    pass

        if not chunks:
            return np.zeros((0,), dtype=np.int16)

        audio = np.concatenate(chunks, axis=0)
        if channels == 1:
            audio = audio[:, 0]
        return audio.astype(np.int16)

    def write_pcm16_wav(self, audio: np.ndarray, path: Path, sample_rate: int = 16000) -> None:
        with wave.open(str(path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(audio.tobytes())

    async def transcribe(self, audio: np.ndarray) -> str:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = Path(f.name)

        try:
            await asyncio.to_thread(self.write_pcm16_wav, audio, wav_path, 16000)
            async with MLX_LOCK:
                result = await asyncio.to_thread(self.local_stt.generate, str(wav_path))
            return (getattr(result, "text", "") or "").strip()
        finally:
            try:
                wav_path.unlink(missing_ok=True)
            except Exception:
                pass

    def ask_ollama_sync(self, prompt: str) -> str:
        if self.args is not None and self.args.utilize_remote:
            messages = [
            {
                'role': 'user',
                'content': prompt,
            },
            ]

            result = "I am voice ai developed at santa cruz."
            for part in self.ollama_client.chat('gpt-oss:120b', messages=messages, stream=True):
                result += part['message']['content']

            # r.json()["response"].strip()
            return self.clean_for_tts(result.strip())
        else:
            r = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": (
                        "You are a helpful voice AI assistant. "
                        "Keep responses concise, clear, and natural for speech.\n\n"
                        f"User: {prompt}\nAssistant:"
                    ),
                    "stream": False,
                },
                timeout=120,
            )
            r.raise_for_status()
            return r.json()["response"].strip()

    async def ask_ollama(self, prompt: str) -> str:
        return await asyncio.to_thread(self.ask_ollama_sync, prompt)

    def synthesize_sync(self, text: str):
        out_audio = None
        for result in self.local_tts.generate(text, voice=os.getenv("LOCAL_TTS_VOICE", LOCAL_TTS_VOICE)):
            out_audio = result.audio
        return out_audio

    async def synthesize(self, text: str):
        async with MLX_LOCK:
            return await asyncio.to_thread(self.synthesize_sync, text)

    def play_audio(self, audio_np, sample_rate: int = 24000) -> None:
        if audio_np is None:
            return

        audio_np = np.asarray(audio_np)
        if audio_np.ndim > 1:
            audio_np = audio_np.squeeze()

        if audio_np.dtype == np.int16:
            playback = audio_np.astype(np.float32) / 32767.0
        else:
            playback = audio_np.astype(np.float32)
            playback = np.clip(playback, -1.0, 1.0)

        sd.play(playback, samplerate=sample_rate)
        sd.wait()

    def clean_for_tts(self,text: str) -> str:
        # Remove markdown emphasis/code
        text = re.sub(r'[`*_#>-]+', ' ', text)

        # Remove simple markdown table lines
        text = re.sub(r'^\|.*\|$', ' ', text, flags=re.MULTILINE)
        text = re.sub(r'^\|?[-: ]+\|[-|: ]*$', ' ', text, flags=re.MULTILINE)

        # Replace URLs with a simple placeholder or remove
        text = re.sub(r'https?://\S+', ' ', text)

        # Collapse repeated whitespace/newlines
        text = re.sub(r'\s+', ' ', text).strip()

        return text


async def main():
    assistant = VoiceAssistant()

    print("Voice assistant")
    print("Press 1 then Enter to start recording")
    print("Press 2 then Enter to stop recording")
    print("Press q then Enter to quit")

    while True:
        cmd = input("\nCommand: ").strip().lower()

        if cmd == "q":
            print("Bye.")
            break

        if cmd != "1":
            print("Press 1 to start, or q to quit.")
            continue

        audio = await asyncio.to_thread(assistant.record_until_stop, 16000, 1)
        if len(audio) == 0:
            print("No audio captured.")
            continue

        print("Transcribing...")
        text = await assistant.transcribe(audio)
        if not text:
            print("No speech detected.")
            continue

        print(f"You: {text}")

        print("Thinking...")
        reply = await assistant.ask_ollama(text)
        print(f"Assistant: {reply}")

        print("Speaking...")
        audio_reply = await assistant.synthesize(reply)
        try:    
            await asyncio.to_thread(assistant.play_audio, audio_reply, 24000)
        except Exception as e:
            print(f"Error during audio playback: {e}")

if __name__ == "__main__":
    asyncio.run(main())