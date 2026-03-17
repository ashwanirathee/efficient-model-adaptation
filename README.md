# Efficient Model Adaptation — PEFT-VQA

This repository is currently focused on one project: a domain-specialized technical VQA assistant for computer vision, machine learning, and computer graphics.

## Project Focus

Build a grounded assistant that answers technical questions by combining:

- retrieval-augmented generation (RAG)
- parameter-efficient fine-tuning (LoRA-first)
- quantized inference for efficient deployment

Core flow:

`question -> retrieve evidence -> reason with adapted model -> grounded answer`

## Scope

- concept explanation and method comparison
- paper and loss-function summarization
- code/debug-oriented technical support
- practical recommendations (dataset, metric, model choices)

## Primary Files

- Orientation + roadmap: [AGENTS.md](AGENTS.md)
- Narrative + backlog snapshot: [docs/writeup.tex](docs/writeup.tex)

## Execution Principles

- measurable: fixed metrics and ablation matrix
- efficient: PEFT and quantization tradeoff tracking
- reproducible: versioned configs, checkpoints, and reports