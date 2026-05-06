from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
import PyPDF2
import requests

load_dotenv()

app = FastAPI()

# 🔥 Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔥 Global storage
document_text = ""

# 🔑 Your OpenRouter API key
API_KEY = os.getenv("OPENROUTER_API_KEY")


@app.get("/")
def home():
    return {"message": "Backend is running 🚀"}


# 🔥 Summarization function
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


# 🔥 Q&A function
def ask_ai(question, text):

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
                "content": f"""
                Answer the question based ONLY on this legal document.

                Document:
                {text[:4000]}

                Question:
                {question}
                """
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    result = response.json()

    if "choices" in result:
        return result["choices"][0]["message"]["content"]

    return f"API Error: {result}"


# 🔥 Upload endpoint
@app.post("/upload")
def upload_file(file: UploadFile = File(...)):

    global document_text

    reader = PyPDF2.PdfReader(file.file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text

    # Save extracted text globally
    document_text = text

    if not text:
        return {"error": "No text extracted from PDF"}

    summary = summarize_text(text)

    return {"summary": summary}


# 🔥 Q&A endpoint
@app.post("/ask")
def ask_question(question: str):

    global document_text

    if not document_text:
        return {"error": "No document uploaded"}

    answer = ask_ai(question, document_text)

    return {"answer": answer}