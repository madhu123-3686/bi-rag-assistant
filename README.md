# Business Intelligence RAG Assistant

A hybrid AI-powered Business Intelligence assistant built using:

- FastAPI
- FAISS (vector database)
- Sentence Transformers (embeddings)
- FLAN-T5 (local LLM)
- Pandas (deterministic analytics)

## Features

- CSV upload
- Persistent FAISS vector storage
- RAG-based question answering
- Deterministic KPI calculations
- Hybrid AI architecture
- Fully local (no external APIs)

## Architecture

Upload CSV → Embeddings → FAISS → Retrieval → LLM Generation

For numerical KPIs:
Pandas deterministic logic + LLM explanation

## Endpoints

- POST /upload
- POST /ask
- GET /highest-revenue
- GET /summary

## Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload

Open:
http://127.0.0.1:8000/docs