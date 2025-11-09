# Trustable LLM Red-Team

**Short summary.**  
This repository is a lightweight, local-first baseline for systematically testing large language models (LLMs) for trustworthiness, safety, and explainability via automated red-team style prompt attacks. The initial focus is a prompt-injection benchmark and lightweight explainability scaffolding for locally-run open models (e.g., Mistral-7B).

**What this repo provides**
- Minimal loader for local inference (supports 4-bit bitsandbytes quantization when GPU available).
- A prompt-injection test runner that executes a set of prompts, flags simple policy violations, and writes results to CSV.
- A small example prompt set and a reproducible repo skeleton ready for extension.
- Guidance for expanding to additional tests (reasoning, factual consistency, chain-of-thought leaks, alignment checks) and different models.

**Quick start (recommended with a CUDA-enabled GPU)**
```bash
python -m venv venv
# macOS / Linux
source venv/bin/activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1

pip install -r requirements.txt

# Run prompt injection test (writes CSV to results/)
python scripts/injection_test.py --out results/injection_run.csv
