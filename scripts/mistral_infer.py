# scripts/mistral_infer.py
"""
Simple model loader + inference helper for locally-run LLMs.
- Attempts to load the specified model in 4-bit (bitsandbytes) when a CUDA device is available.
- Falls back to a standard HF load on failure.
- Exposes `ask(prompt, max_new_tokens)` for simple prompt-response inference.
Environment:
- Set model override: $env:TRUST_MODEL = "hf-username/model-name"
"""

import os
import warnings
from typing import Tuple

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import BitsAndBytesConfig

# Default HF model (change via TRUST_MODEL env var or in code)
MODEL = os.environ.get("TRUST_MODEL", "mistralai/Mistral-7B-Instruct-v0.1")

_tokenizer = None
_model = None

def load_model() -> Tuple[object, object]:
    """
    Try loading the model using bitsandbytes 4-bit quantization if CUDA is available.
    If any error occurs, fallback to a normal (float32) load.
    Returns (tokenizer, model).
    """
    global MODEL
    # First load tokenizer (cheap)
    print(f"[loader] Loading tokenizer for {MODEL} ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL, use_fast=False)

    # Try 4-bit quantized load if CUDA available
    if torch.cuda.is_available():
        try:
            print("[loader] CUDA detected  attempting 4-bit bitsandbytes load ...")
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                # use bfloat16 on capable GPUs to improve stability if supported by torch
                bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
            )
            model = AutoModelForCausalLM.from_pretrained(
                MODEL,
                device_map="auto",
                quantization_config=bnb_config,
                trust_remote_code=True
            )
            print("[loader] Model loaded with bitsandbytes 4-bit quantization.")
            return tokenizer, model
        except Exception as e:
            warnings.warn(f"[loader] 4-bit load failed: {e}. Falling back to standard load.")
    else:
        print("[loader] No CUDA device detected  performing standard load (may be CPU-only & slow).")

    # Fallback load (may be heavy)
    model = AutoModelForCausalLM.from_pretrained(MODEL, device_map="auto", trust_remote_code=True)
    print("[loader] Model loaded (standard precision).")
    return tokenizer, model

def ensure_model():
    """Load model and tokenizer if not already loaded."""
    global _tokenizer, _model
    if _model is None or _tokenizer is None:
        _tokenizer, _model = load_model()

def ask(prompt: str, max_new_tokens: int = 256) -> str:
    """
    Run the model on the prompt and return a decoded string.
    Moves inputs to the device the model is on.
    """
    ensure_model()
    device = next(_model.parameters()).device
    inputs = _tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        out = _model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
    text = _tokenizer.decode(out[0], skip_special_tokens=True)
    return text

if __name__ == "__main__":
    # quick local smoke test
    ensure_model()
    print(ask("Write a concise summary of Occam's razor in one paragraph.", max_new_tokens=200))
