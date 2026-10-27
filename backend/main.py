from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import PyPDF2
import requests
import numpy as np
from sentence_transformers import SentenceTransformer  # NEW: local embedding model
import faiss                                            # NEW: vector search library

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global storage ---
document_text = ""
faiss_index = None   # NEW: will hold our searchable vector database
chunks = []          # NEW: will hold the split-up pieces of the document

# NEW: Load the embedding model once when the server starts
# "all-MiniLM-L6-v2" is a small (~90MB), fast model that runs 100% locally
# It converts any text into a list of 384 numbers that represent its meaning
# First run will download it automatically — after that it's cached
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

API_KEY = os.getenv("OPENROUTER_API_KEY")


@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# ============================================================
# NEW FUNCTION 1: Chunking
# ============================================================
# Why do we chunk?
# A legal PDF can be 50+ pages. Sending all of it to the LLM at once
# is too expensive (or impossible). So we cut it into small pieces.
# When a question comes in, we only send the RELEVANT pieces — not everything.

def chunk_text(text, chunk_size=500, overlap=50):
    # chunk_size=500 → each piece is ~500 characters (roughly 2-3 paragraphs)
    # overlap=50 → each chunk shares 50 characters with the next one
    # Why overlap? So that if an important sentence falls right at the border
    # of two chunks, it doesn't get cut in half and lost

    result = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]   # grab one piece of text
        result.append(chunk)
        # Move forward, but step back by 'overlap' so next chunk re-reads the tail
        start += chunk_size - overlap

    return result


# ============================================================
# NEW FUNCTION 2: Build the FAISS index
# ============================================================
# Why FAISS?
# Imagine you have 200 chunks. When a user asks a question,
# you don't want to send all 200 to the LLM — that's too slow and costly.
# FAISS lets you say: "give me the 5 chunks most similar to this question"
# in milliseconds. It searches by meaning, not just keywords.

def build_faiss_index(text_chunks):
    # Step 1: Convert every chunk of text into a vector (list of 384 numbers)
    # Each number captures some aspect of the text's meaning
    embeddings = embedding_model.encode(text_chunks)

    # Step 2: FAISS requires float32 format — numpy handles the conversion
    embeddings = np.array(embeddings).astype("float32")

    # Step 3: Get the length of each vector (384 for this model)
    dimension = embeddings.shape[1]

    # Step 4: Create a FAISS index using L2 distance
    # L2 = Euclidean distance between two vectors
    # Smaller distance = more similar meaning
    index = faiss.IndexFlatL2(dimension)

    # Step 5: Add all chunk vectors into the index
    index.add(embeddings)

    return index


# ============================================================
# NEW FUNCTION 3: Find relevant chunks for a question
# ============================================================
# This is the "Retrieval" part of RAG (Retrieval Augmented Generation)
# We embed the user's question the same way we embedded the chunks,
# then ask FAISS: "which chunks are closest in meaning to this question?"

def get_relevant_chunks(question, index, text_chunks, top_k=5):
    # Convert the question into a vector using the same model
    question_vector = embedding_model.encode([question])
    question_vector = np.array(question_vector).astype("float32")

    # Search the FAISS index for the top_k most similar chunks
    # D = distances (how similar each result is)
    # I = indices (the position of each matching chunk in our list)
    D, I = index.search(question_vector, top_k)

    # Use the indices to fetch the actual text of the matching chunks
    relevant = [text_chunks[i] for i in I[0] if i < len(text_chunks)]

    return relevant


# ============================================================
# UNCHANGED: Summarization (still works the same way)
# ============================================================
def summarize_text(text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": f"Summarize this legal document clearly:\n\n{text[:4000]}"
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"API Error: {result}"


# ============================================================
# UPDATED: ask_ai now uses only the relevant chunks, not full doc
# ============================================================
# This is the "Augmented Generation" part of RAG.
# Instead of dumping the whole document into the prompt (and hitting the 4000 char limit),
# we only send the 5 most relevant chunks — which is much more focused and accurate.

def ask_ai_with_context(question, relevant_chunks):
    # Join the retrieved chunks into one context block
    context = "\n\n---\n\n".join(relevant_chunks)

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "user",
                "content": f"""You are a legal assistant. Answer the question using ONLY the document excerpts below.
If the answer is not in the excerpts, say "I couldn't find that in the document."

Relevant excerpts from the document:
{context}

Question: {question}"""
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return f"API Error: {result}"


# ============================================================
# UPDATED: /upload endpoint now also builds the RAG index
# ============================================================
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    global document_text, faiss_index, chunks

    reader = PyPDF2.PdfReader(file.file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    if not text:
        return {"error": "No text extracted from PDF"}

    document_text = text

    # NEW: Split the full document into chunks
    chunks = chunk_text(text)

    # NEW: Convert all chunks to vectors and store in FAISS
    faiss_index = build_faiss_index(chunks)

    # Summarize as before
    summary = summarize_text(text)

    return {
        "summary": summary,
        "chunks_created": len(chunks)  # handy debug info — tells you how many pieces were made
    }


# ============================================================
# UPDATED: /ask now uses RAG instead of raw text
# ============================================================
@app.post("/ask")
def ask_question(question: str):
    global faiss_index, chunks

    if not chunks:
        return {"error": "No document uploaded yet. Please upload a PDF first."}

    # Find the 5 most relevant chunks for this question
    relevant_chunks = get_relevant_chunks(question, faiss_index, chunks)

    # Send only those chunks to the LLM
    answer = ask_ai_with_context(question, relevant_chunks)

    return {"answer": answer}