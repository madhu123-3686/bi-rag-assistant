import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from app.hf_llm import query_llm


# ---------------------------
# Initialize Embedding Model
# ---------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

INDEX_PATH = "faiss_index"


# ---------------------------
# Create & Save Vector Store
# ---------------------------

def create_vector_store(text: str):
    """
    Creates FAISS vector store from text
    and saves it locally.
    """

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.create_documents([text])

    vectorstore = FAISS.from_documents(docs, embeddings)

    # Save locally
    vectorstore.save_local(INDEX_PATH)

    return vectorstore


# ---------------------------
# Load Existing Vector Store
# ---------------------------

def load_vector_store():
    """
    Loads FAISS index if it exists.
    """

    if os.path.exists(INDEX_PATH):
        return FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    return None


# ---------------------------
# Add New Data to Existing Index
# ---------------------------

def add_to_vector_store(vectorstore, text: str):
    """
    Adds new documents to existing FAISS index.
    """

    splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = splitter.create_documents([text])

    vectorstore.add_documents(docs)

    vectorstore.save_local(INDEX_PATH)

    return vectorstore


# ---------------------------
# Generate Answer using RAG
# ---------------------------

def generate_answer(vectorstore, question: str):
    """
    Retrieves relevant chunks and generates answer
    """

    retriever = vectorstore.as_retriever()

    docs = retriever.invoke(question)

    # Extract only text content
    context_chunks = [doc.page_content for doc in docs]

    context = "\n".join(context_chunks)

    prompt = f"""
You are a Business Intelligence assistant.

Use the context below to answer the question.

Context:
{context}

Question:
{question}

Give a short business answer.
"""

    answer = query_llm(prompt)

    return {
        "answer": answer,
        "sources": context_chunks
    }
