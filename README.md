# Legal AI Assistant

An AI-powered web application that allows users to upload legal PDF documents, generate concise summaries, and ask natural language questions about the document using a **RAG (Retrieval-Augmented Generation)** pipeline.

---

## Features

* Upload legal PDF documents
* Extract text from all pages of the PDF
* Generate AI-based plain-English summaries
* Ask questions — answered from the **entire document** using semantic search, not just the first few pages
* Markdown-rendered responses (bold, bullet points formatted correctly)
* Minimal and responsive React frontend
* FastAPI backend with REST API architecture
* OpenRouter AI integration (free tier, no credit card required)

---

## Tech Stack

### Frontend
* React.js
* Axios
* react-markdown
* CSS

### Backend
* FastAPI (Python)
* PyPDF2 — PDF text extraction
* sentence-transformers (`all-MiniLM-L6-v2`) — local embedding model, runs on CPU, no API cost
* FAISS (`faiss-cpu`) — vector similarity search
* NumPy — vector format conversion
* OpenRouter API — free LLM gateway
* python-dotenv — secure API key management

---

## How It Works (RAG Pipeline)

```
User uploads PDF
      ↓
Extract all text (PyPDF2)
      ↓
Split text into 500-char chunks with 50-char overlap
      ↓
Convert each chunk to a 384-dimension vector (sentence-transformers)
      ↓
Store all vectors in FAISS index (in-memory vector search)
      ↓
Return AI summary to user (first 4000 chars → OpenRouter LLM)

User asks a question
      ↓
Convert question to vector (same embedding model)
      ↓
FAISS finds top-5 most semantically similar chunks
      ↓
Top-5 chunks + question → OpenRouter LLM
      ↓
Return grounded answer to user
```

The RAG approach means answers are drawn from the **entire document**, not just the beginning — and the LLM only sees relevant sections, making responses more accurate and focused.

---

## Project Structure

```
legal-ai-project/
│
├── backend/
│   ├── main.py              # FastAPI app with RAG pipeline
│   ├── requirements.txt
│   ├── .gitignore
│   └── .env                 # API key (not committed to GitHub)
│
├── frontend/
│   ├── src/
│   │   └── App.js           # React UI with markdown rendering
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

---

## Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/adeeba-here/legal_doc_summarizer.git
cd legal_doc_summarizer
```

---

### Backend Setup

#### Navigate to backend
```bash
cd backend
```

#### Create and activate virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

> **Note:** First run will download the sentence-transformer model (~90MB). This is a one-time download — it is cached locally after that.

#### Create `.env` file
Create a `.env` file inside the `backend/` folder:
```env
OPENROUTER_API_KEY=your_api_key_here
```
Get a free API key at [openrouter.ai](https://openrouter.ai) — no credit card required.

#### Run backend server
```bash
uvicorn main:app --reload
```
Backend runs at: `http://127.0.0.1:8000`
API docs available at: `http://127.0.0.1:8000/docs`

---

### Frontend Setup

#### Navigate to frontend
```bash
cd frontend
```

#### Install dependencies
```bash
npm install
```

#### Start frontend
```bash
npm start
```
Frontend runs at: `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/upload` | Upload PDF → returns summary + chunks_created |
| POST | `/ask?question=...` | Ask a question → returns grounded answer |

### Example Response — `/upload`
```json
{
  "summary": "This agreement is between Alpha Corporate Solutions...",
  "chunks_created": 47
}
```

### Example Response — `/ask`
```json
{
  "answer": "According to Section 7, either party may terminate with 30 days written notice..."
}
```

---

## Sample Questions to Try

* What is the agreement duration?
* What is the penalty clause?
* Who governs the agreement?
* What are the payment terms?
* What happens if payment is late?
* Under what conditions can the contract be terminated immediately?

---

## Future Improvements

* Persistent FAISS index (survive server restarts)
* Multiple document support with session management
* User authentication
* Chat history
* Dark mode UI
* Map-reduce summarization for very long documents
* OCR support for scanned PDFs

---

## Notes

* Internet connection is required for LLM responses (OpenRouter API).
* The embedding model runs **locally** — no internet needed for that part.
* Backend server must be running while using the frontend.
* Only digitally-created PDFs are supported (not scanned image PDFs).
* `.env` file is excluded from GitHub via `.gitignore` — never commit your API key.

---

## Author

Developed as a Python Backend Developer Intern project at Rooman Technologies.
Built with React, FastAPI, FAISS, sentence-transformers, and OpenRouter AI.