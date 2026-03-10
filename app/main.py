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
dataframes = []


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

    # Convert to text
    text_data = dataframe_to_text(df)

    # Update vector store
    if vectorstore:
        vectorstore = add_to_vector_store(vectorstore, text_data)
    else:
        vectorstore = create_vector_store(text_data)

    return JSONResponse(
        content={"message": "File processed and indexed successfully"}
    )


# -----------------------------
# Ask Question Endpoint
# -----------------------------

@app.post("/ask")
async def ask_question(question: str):
    global vectorstore, dataframes

    if not dataframes:
        raise HTTPException(status_code=400, detail="Upload CSV first.")

    df = pd.concat(dataframes, ignore_index=True)

    q = question.lower()

    # -----------------------------
    # Highest Revenue Product
    # -----------------------------

    if "highest revenue" in q or "top product" in q:

        row = df.loc[df["Revenue"].idxmax()]

        return {
            "answer": f"{row['Product']} generated the highest revenue ({row['Revenue']}).",
            "sources": [row.to_dict()]
        }

    # -----------------------------
    # Lowest Revenue Product
    # -----------------------------

    if "lowest revenue" in q:

        row = df.loc[df["Revenue"].idxmin()]

        return {
            "answer": f"{row['Product']} generated the lowest revenue ({row['Revenue']}).",
            "sources": [row.to_dict()]
        }

    # -----------------------------
    # Total Revenue
    # -----------------------------

    if "total revenue" in q:

        total = int(df["Revenue"].sum())

        return {
            "answer": f"The total revenue is {total}.",
            "sources": df.to_dict(orient="records")
        }

    # -----------------------------
    # Region Performance
    # -----------------------------

    if "region" in q and "best" in q:

        region_revenue = df.groupby("Region")["Revenue"].sum()

        best_region = region_revenue.idxmax()
        best_value = int(region_revenue.max())

        return {
            "answer": f"{best_region} performs best with total revenue of {best_value}.",
            "sources": df.to_dict(orient="records")
        }

    # -----------------------------
    # Chart Requests
    # -----------------------------

    if "chart" in q or "plot" in q or "visualize" in q or "graph" in q:

        revenue_data = df.groupby("Product")["Revenue"].sum().reset_index()

        return {
            "type": "chart",
            "products": revenue_data["Product"].tolist(),
            "revenues": revenue_data["Revenue"].tolist()
        }
     # Business summary
    if "summary" in q or "business summary" in q:
        total_revenue = int(df["Revenue"].sum())
        avg_revenue = round(float(df["Revenue"].mean()), 2)

        top_row = df.loc[df["Revenue"].idxmax()]
        best_product = str(top_row["Product"])

        region_revenue = df.groupby("Region")["Revenue"].sum()
        best_region = region_revenue.idxmax()

        return {
             "answer": f"""
    Business Summary:

    • Total Revenue: {total_revenue}
    • Average Revenue: {avg_revenue}
    • Top Product: {best_product}
    • Best Performing Region: {best_region}
    """,
            "sources": df.to_dict(orient="records")
        }

    # -----------------------------
    # RAG Fallback
    # -----------------------------

    result = generate_answer(vectorstore, question)

    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }


# -----------------------------
# Highest Revenue Endpoint
# -----------------------------

@app.get("/highest-revenue")
def highest_revenue():
    global dataframes

    if not dataframes:
        raise HTTPException(status_code=400, detail="No data uploaded.")

    df = pd.concat(dataframes, ignore_index=True)

    max_row = df.loc[df["Revenue"].idxmax()]

    product = str(max_row["Product"])
    revenue = int(max_row["Revenue"])

    return {
        "product": product,
        "revenue": revenue
    }


# -----------------------------
# Business Summary
# -----------------------------

@app.get("/summary")
def get_summary():
    global vectorstore

    if not vectorstore:
        raise HTTPException(status_code=400, detail="No data indexed.")

    summary_prompt = "Provide a professional business summary of the indexed data."

    result = generate_answer(vectorstore, summary_prompt)

    return {"summary": result["answer"]}


# -----------------------------
# Revenue Chart Data
# -----------------------------

@app.get("/revenue-chart")
def revenue_chart():
    global dataframes

    if not dataframes:
        raise HTTPException(status_code=400, detail="No data uploaded.")

    df = pd.concat(dataframes, ignore_index=True)

    revenue_data = df.groupby("Product")["Revenue"].sum().reset_index()

    return {
        "products": revenue_data["Product"].tolist(),
        "revenues": revenue_data["Revenue"].tolist()
    }


# -----------------------------
# Business Insights
# -----------------------------

@app.get("/insights")
def insights():
    global dataframes

    if not dataframes:
        raise HTTPException(status_code=400, detail="No data uploaded.")

    df = pd.concat(dataframes, ignore_index=True)

    top_row = df.loc[df["Revenue"].idxmax()]
    low_row = df.loc[df["Revenue"].idxmin()]

    insights = [
        f"Top product: {top_row['Product']} ({top_row['Revenue']})",
        f"Lowest revenue product: {low_row['Product']}",
        f"Total revenue: {int(df['Revenue'].sum())}",
        f"Average revenue: {round(float(df['Revenue'].mean()), 2)}",
        f"Number of products: {int(df['Product'].nunique())}"
    ]

    return {"insights": insights}