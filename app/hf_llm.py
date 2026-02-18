from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_name = "google/flan-t5-small"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def query_llm(prompt: str) -> str:
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

        outputs = model.generate(
            **inputs,
            max_new_tokens=128,
            do_sample=False
        )

        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result

    except Exception as e:
        return f"Local Model Error: {str(e)}"
