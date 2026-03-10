from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

model_name = "google/flan-t5-base"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

def query_llm(prompt: str) -> str:
    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

        outputs = model.generate(
            **inputs,
            max_new_tokens=80,
            do_sample=False,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3
        )

        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return result

    except Exception as e:
        return f"Local Model Error: {str(e)}"
