---
name: repo-orientation
description: "Use when: navigating the efficient-model-adaptation workspace, summarizing subprojects (PEFT-VQA, PEFT-thyroid, MLX voice), or answering onboarding questions about structure, workflows, or docs."
---

# Efficient Model Adaptation — Repo Orientation Skill

## What this skill does

- Answers "where is X?" and "how do I work on Y?" questions without re-parsing the entire tree.
- Highlights the flagship efforts (technical VQA assistant, thyroid PEFT study, MLX voice runtime) plus the docs that describe them.
- Points directly to [AGENTS.md](AGENTS.md), subproject READMEs, and [docs/writeup.tex](docs/writeup.tex) so new agents can ramp fast.

## How to run the workflow

1. **Review the brief** by skimming this skill plus the roadmap snapshot in [docs/writeup.tex](docs/writeup.tex).
2. **Select the subproject**:
   - PEFT-VQA planning → [docs/writeup.tex](docs/writeup.tex#L20-L60) for personas/tasks and [src/peft-vqa/](src/peft-vqa/) for upcoming code and datasets.
   - PEFT-Thyroid study → [src/peft-thyroid/README.md](src/peft-thyroid/README.md) and the Kaggle notebooks it references.
   - MLX Voice AI runtime → [app/voice-ai/readme.md](app/voice-ai/readme.md) for install/run steps and tuning knobs.
3. **Match the request type**:
   - Implementation help → inspect the relevant subdirectory source files or notebooks.
   - Roadmap/status → quote from [docs/writeup.tex](docs/writeup.tex) (Mission, Completed Work, In-Flight sections).
   - Evaluation/logging → record findings directly in [docs/writeup.tex](docs/writeup.tex) or the pertinent README; there is no dedicated eval harness yet.
4. **Report back with links** using the file/line linkification rules so collaborators can jump straight to sources.

## Tips & Constraints

- Keep ASCII; avoid touching generated artifacts (models/, **pycache**/).
- Thyroid notebooks are Kaggle-first; remind users to attach the referenced datasets and LoRA/BitFit weights instead of running locally.
- Document interim eval runs or qualitative findings in [docs/writeup.tex](docs/writeup.tex) until a scripted harness exists.
- Keep responses grounded in engineering readiness so automation can act on them immediately.

## Related Assets

- Program brief + roadmap: [docs/writeup.tex](docs/writeup.tex)
- Agent playbook (setup + commands): [AGENTS.md](AGENTS.md)
- Medical PEFT assets: [src/peft-thyroid/assets/](src/peft-thyroid/assets/)
- Voice runbook: [app/voice-ai/readme.md](app/voice-ai/readme.md)

## Quickstart Cheatsheet

- **PEFT-VQA**: `cd src/peft-vqa && python -m venv .venv && source .venv/bin/activate && pip install -r ../../requirements.txt`; track personas/tasks in [docs/writeup.tex](docs/writeup.tex) and drop prototypes inside this folder.
- **PEFT-Thyroid**: Open the Kaggle-ready notebooks under [src/peft-thyroid/](src/peft-thyroid/) and follow the README directions for attaching DDTI datasets and LoRA/BitFit weights before running.
- **MLX Voice AI**: `cd app/voice-ai && uv sync`, install Homebrew deps (`brew install espeak-ng portaudio ffmpeg`), then launch with `ESPEAK_DATA_PATH="$(brew --prefix espeak-ng)/share/espeak-ng-data" uv run src/agent.py` (overrides live in `.env.local`).
- **Writeup PDF**: `cd docs && latexmk -pdf writeup.tex` to compile the narrative after any documentation edits.

## Repeatable Workflows

- **Update the LaTeX writeup**
  1. Edit [docs/writeup.tex](docs/writeup.tex) (Mission, Completed, Planned, Roadmap sections).
  2. Keep tables synced with the latest metrics or qualitative notes; cite new files with linkified references.
  3. Sanity-check formatting with `cd docs && latexmk -pdf writeup.tex` (or run `pdflatex` twice) before publishing.
  4. Reflect any major narrative changes in [AGENTS.md](AGENTS.md) so setup instructions stay aligned.
- **Debug the TTS stack**
  1. Verify Homebrew deps: `brew list espeak-ng portaudio ffmpeg`; reinstall if missing.
  2. Confirm phoneme tables: `ls $(brew --prefix espeak-ng)/share/espeak-ng-data/phontab`.
  3. Export `ESPEAK_DATA_PATH` (or `ESPEAKNG_DATA`) before `uv run src/agent.py`; note the path in `.env.local` if it should persist.
  4. Re-run the voice agent with `LOGLEVEL=DEBUG` (set via env var) to capture Kokoro warnings and document fixes in [app/voice-ai/readme.md](app/voice-ai/readme.md).

Use this skill whenever an agent needs to ground itself before editing or summarizing any part of the repository.
