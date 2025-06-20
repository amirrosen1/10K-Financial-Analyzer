import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from constants import HUGGINGFACE_TOKEN

folder = os.path.join(os.path.dirname(__file__), '..', 'output', 'query_results_v2', 'total_revenue')
folder = os.path.abspath(folder)

model_name = "mistralai/Mistral-7B-Instruct-v0.3"


_model, _tokenizer = None, None

def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        _tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_TOKEN)
        if _tokenizer.pad_token is None:
            _tokenizer.pad_token = _tokenizer.eos_token
        _model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            token=HUGGINGFACE_TOKEN
        )
    return _model, _tokenizer

def init_model(model_name = "mistralai/Mistral-7B-Instruct-v0.3"):
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_TOKEN)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        token=HUGGINGFACE_TOKEN
    )
    return model,tokenizer


def invoke_model(prompt):
    model, tokenizer = get_model_and_tokenizer()
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=True,
            temperature=0.3
        )
    return tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True).strip()
