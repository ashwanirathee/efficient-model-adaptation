# Efficient Model Adaptation — Agent Playbook

## Setup Checklist
| Track | Environment Prep | One-time Notes |
|-------|------------------|----------------|
| PEFT-VQA | `cd src/peft-vqa && python -m venv .venv && source .venv/bin/activate && pip install -r ../../requirements.txt` | Keep `.env` placeholders ready for retrieval endpoints once adapters land. |
| PEFT-Thyroid | Kaggle notebook runtime per [src/peft-thyroid/README.md](src/peft-thyroid/README.md) | Attach the DDTI dataset + LoRA/BitFit checkpoints before execution. |
| MLX Voice Agent | `brew install espeak-ng portaudio ffmpeg && uv sync` inside [app/voice-ai](app/voice-ai/readme.md) | Copy overrides into `.env.local`; export `ESPEAK_DATA_PATH="$(brew --prefix espeak-ng)/share/espeak-ng-data"` before launching. |

## Test & Run Commands
- **Writeup sanity check**: `cd docs && latexmk -pdf writeup.tex` to confirm the program narrative still compiles.
- **Writeup line width**: keep manual edits in [docs/writeup.tex](docs/writeup.tex) wrapped at 80 columns so diffs stay readable; only exceed for LaTeX tables if absolutely necessary.
- **Writeup sanity check**: `cd docs && latexmk -pdf writeup.tex` to confirm the program narrative still compiles.
- **Model manifest lint**: `python -m json.tool test.json` before sharing updated eval prompts/responses.
- **PEFT-Thyroid notebooks**: Open Kaggle, import each notebook from [src/peft-thyroid](src/peft-thyroid) and click “Run All”; metrics are logged inline.
- **Voice agent smoke test**: `cd app/voice-ai && ESPEAK_DATA_PATH="$(brew --prefix espeak-ng)/share/espeak-ng-data" uv run src/agent.py`.

## Architecture Map
- **PEFT-VQA**: Currently doc-first—personas, tasks, and roadmap live in [docs/writeup.tex](docs/writeup.tex); future datasets/scripts belong under [src/peft-vqa](src/peft-vqa).
- **PEFT-Thyroid**: Dataset prep → baseline → LoRA/BitFit tuning → evaluation via the notebook quartet (`dataset`, `baseline`, `training`, `testing`) in [src/peft-thyroid](src/peft-thyroid); artifacts referenced in the README.
- **MLX Voice Agent**: [app/voice-ai/src/agent.py](app/voice-ai/src/agent.py#L1-L170) orchestrates Parakeet STT, Ollama inference, and Kokoro TTS with the shared `MLX_LOCK` plus `sounddevice` playback; `.env.local` toggles models/endpoints.

## Coding Conventions
- Keep config in `.env.local` or Justfile variables; avoid hardcoding secrets.
- Prefer `uv` for dependency isolation; when adding libraries update `pyproject.toml`/`requirements.txt` through reproducible commands (e.g., `uv pip compile`).
- Never edit Kaggle `.ipynb` via non-notebook tooling without documenting the process; ensure metadata stays intact.
- Enforce ASCII-only edits unless the file already uses Unicode symbols for math.
- Log interim eval findings inside [docs/writeup.tex](docs/writeup.tex) or the relevant README until a scripted harness exists.

## Validation Hooks
- Run `cd docs && latexmk -pdf writeup.tex` after every roadmap or narrative tweak.
- For the voice agent, capture sample transcripts + latencies in [app/voice-ai/readme.md](app/voice-ai/readme.md) when changing models or audio settings.
- For the thyroid notebooks, re-run the Kaggle “testing” notebook before publishing new metrics and update the README tables accordingly.

Refer to [SKILL.md](SKILL.md) for day-to-day workflows and escalation paths.
