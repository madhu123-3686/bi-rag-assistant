import os
import shutil
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from app.data_loader import load_csv, dataframe_to_text
from app.rag_pipeline import (
    create_vector_store,
    load_vector_store,
    add_to_vector_store,
    generate_answer
)

app = FastAPI(title="Business Intelligence RAG Assistant")

# -----------------------------
# Global Storage
# -----------------------------

vectorstore = load_vector_store()
dataframes = []  # store uploaded dataframes


# -----------------------------
# Root Endpoint
# -----------------------------

@app.get("/")
def home():
    return {"message": "Business Intelligence Assistant API is running"}


# -----------------------------
# Upload CSV Endpoint
# -----------------------------

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    global vectorstore, dataframes

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    os.makedirs("temp", exist_ok=True)
    file_path = os.path.join("temp", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Load CSV
    df = load_csv(file_path)
    dataframes.append(df)

    # Convert to text for RAG
    text_data = dataframe_to_text(df)

    if vectorstore:
        vectorstore = add_to_vector_store(vectorstore, text_data)
    else:
        vectorstore = create_vector_store(text_data)

    return JSONResponse(content={"message": "File processed and indexed successfully"})


# -----------------------------
# RAG Question Answering
# -----------------------------

@app.post("/ask")
async def ask_question(question: str):
    global vectorstore

    if not vectorstore:
        raise HTTPException(status_code=400, detail="No data indexed. Upload a CSV first.")

    answer = generate_answer(vectorstore, question)

    return {"answer": answer}


# -----------------------------
# Deterministic Highest Revenue Endpoint (Hybrid Logic)
# -----------------------------

@app.get("/highest-revenue")
def highest_revenue():
    global dataframes

    if not dataframes:
        raise HTTPException(status_code=400, detail="No data uploaded.")

    combined_df = pd.concat(dataframes, ignore_index=True)

    if "Revenue" not in combined_df.columns or "Product" not in combined_df.columns:
        raise HTTPException(status_code=400, detail="CSV must contain Product and Revenue columns.")

    max_row = combined_df.loc[combined_df["Revenue"].idxmax()]

    product = str(max_row["Product"])
    revenue = int(max_row["Revenue"])   # ✅ Convert numpy.int64 → int

    explanation_prompt = f"""
    The product {product} generated revenue of {revenue}.
    Provide a short professional business explanation.
    """

    explanation = generate_answer(vectorstore, explanation_prompt)

    return {
        "product": product,
        "revenue": revenue,
        "explanation": explanation
    }



# -----------------------------
# Business Summary Endpoint
# -----------------------------

@app.get("/summary")
def get_summary():
    global vectorstore

    if not vectorstore:
        raise HTTPException(status_code=400, detail="No data indexed.")

    summary_prompt = "Provide a professional business summary of the indexed data."

    summary = generate_answer(vectorstore, summary_prompt)

    return {"summary": summary}
