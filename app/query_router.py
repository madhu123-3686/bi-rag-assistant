from app.hf_llm import query_llm


def classify_query(question: str):

    prompt = f"""
Classify the user query into one of these categories:

1. analytics → numeric calculations
2. visualization → charts or plots
3. rag → explanation from context

Return only one word.

Question: {question}
"""

    response = query_llm(prompt).lower().strip()

    if "visual" in response or "chart" in response:
        return "visualization"

    if "analytic" in response or "number" in response:
        return "analytics"

    return "rag"