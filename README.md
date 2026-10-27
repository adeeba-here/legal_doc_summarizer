# Legal AI Assistant

An AI-powered web application that allows users to upload legal PDF documents, generate concise summaries, and ask questions about the uploaded document using an AI model.

---

# Features

* Upload legal PDF documents
* Extract text from uploaded PDFs
* Generate AI-based summaries
* Ask questions about uploaded documents
* Minimal and responsive React frontend
* FastAPI backend with REST API architecture
* OpenRouter AI integration

---

# Tech Stack

## Frontend

* React.js
* Axios
* CSS

## Backend

* FastAPI
* Python
* REST API
* PyPDF2
* OpenRouter API

---

# Project Structure

```text
legal-ai-project/
│
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .gitignore
│   └── .env
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
└── README.md
```

---

# How It Works

1. User uploads a legal PDF document.
2. Backend extracts text using PyPDF2.
3. Extracted text is sent to OpenRouter AI.
4. AI generates a summary.
5. User can ask questions related to the uploaded document.
6. AI answers using document context.

---

# Installation & Setup

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/legal_doc_summarizer.git
```

---

# Backend Setup

## 1. Navigate to backend

```bash
cd backend
```

## 2. Create virtual environment

```bash
python -m venv venv
```

## 3. Activate virtual environment

### Windows

```bash
venv\Scripts\activate
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Create .env file

Create a `.env` file inside the backend folder.

```env
OPENROUTER_API_KEY=your_api_key_here
```

---

## 6. Run backend server

```bash
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

# Frontend Setup

## 1. Navigate to frontend

```bash
cd frontend
```

## 2. Install dependencies

```bash
npm install
```

---

## 3. Start frontend

```bash
npm start
```

Frontend runs on:

```text
http://localhost:3000
```

---

# API Endpoints

## Upload PDF

```http
POST /upload
```

Uploads a PDF and generates a summary.

---

## Ask Questions

```http
POST /ask
```

Allows users to ask questions related to the uploaded document.

---

# Sample Questions

* What is the agreement duration?
* What is the penalty clause?
* Who governs the agreement?
* What are the payment terms?



---

# Future Improvements

* Multiple PDF support
* User authentication
* Database integration
* Chat history
* Dark mode UI
* Better AI models
* Document storage

---

# Notes

* Internet connection is required for AI responses.
* Backend server must be running while using frontend.
* OpenRouter API key is required inside `.env`.

---

# Author

Developed as an AI-powered legal document summarization and Q&A project using React, FastAPI, and OpenRouter AI.
