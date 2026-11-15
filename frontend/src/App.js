import React, { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [fileName, setFileName] = useState("");
  const [summary, setSummary] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [uploaded, setUploaded] = useState(false);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    if (selected) {
      setFile(selected);
      setFileName(selected.name);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file first.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      setLoadingMessage("Reading your document…");
      setSummary("");
      setAnswer("");

      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      setSummary(response.data.summary);
      setUploaded(true);
    } catch (error) {
      console.error(error);
      alert("Upload failed. Make sure the backend is running.");
    }

    setLoading(false);
    setLoadingMessage("");
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      alert("Please enter a question.");
      return;
    }

    try {
      setLoading(true);
      setLoadingMessage("Finding the answer…");
      setAnswer("");

      const response = await axios.post(
        `http://127.0.0.1:8000/ask?question=${encodeURIComponent(question)}`
      );

      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
      alert("Something went wrong. Make sure the backend is running.");
    }

    setLoading(false);
    setLoadingMessage("");
  };

  return (
    <div className="page">

      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <span className="logo">⚖️</span>
          <span className="brand">LegalAI</span>
        </div>
      </header>

      {/* ── Hero ── */}
      <section className="hero">
        <h1 className="hero-title">Understand any legal document<br />in seconds.</h1>
        <p className="hero-sub">
          Upload a PDF — get a plain-English summary and ask anything about it.
        </p>
      </section>

      {/* ── Main content ── */}
      <main className="main">

        {/* Step 1 — Upload */}
        <section className="section">
          <p className="step-label">Step 1</p>
          <h2 className="section-title">Upload your document</h2>
          <p className="section-sub">Supported format: PDF. The document stays on your machine.</p>

          <label className="upload-zone" htmlFor="file-input">
            {fileName ? (
              <>
                <span className="upload-icon">📄</span>
                <span className="upload-filename">{fileName}</span>
                <span className="upload-change">Tap to change</span>
              </>
            ) : (
              <>
                <span className="upload-icon">⬆️</span>
                <span className="upload-cta">Choose a PDF file</span>
                <span className="upload-hint">Tap to browse</span>
              </>
            )}
            <input
              id="file-input"
              type="file"
              accept="application/pdf"
              onChange={handleFileChange}
              className="file-input-hidden"
            />
          </label>

          <button
            className={`btn-primary ${!file ? "btn-disabled" : ""}`}
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading && loadingMessage.includes("Reading") ? loadingMessage : "Summarise Document"}
          </button>
        </section>

        {/* Loading indicator */}
        {loading && (
          <div className="loading-row">
            <span className="spinner" />
            <span className="loading-text">{loadingMessage}</span>
          </div>
        )}

        {/* Step 2 — Summary */}
        {summary && (
          <section className="section fade-in">
            <p className="step-label">Step 2</p>
            <h2 className="section-title">Summary</h2>
            <div className="result-box">
              <ReactMarkdown>{summary}</ReactMarkdown>
            </div>
          </section>
        )}

        {/* Step 3 — Q&A (only appears after upload) */}
        {uploaded && (
          <section className="section fade-in">
            <p className="step-label">Step 3</p>
            <h2 className="section-title">Ask a question</h2>
            <p className="section-sub">
              Try: "What is the notice period?" or "What happens if payment is late?"
            </p>

            <div className="input-row">
              <input
                className="text-input"
                type="text"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  // Submit on Enter key — no need to click the button
                  if (e.key === "Enter") askQuestion();
                }}
                placeholder="Ask anything about this document…"
              />
              <button
                className="btn-primary btn-ask"
                onClick={askQuestion}
                disabled={loading}
              >
                {loading && loadingMessage.includes("Finding") ? "…" : "Ask"}
              </button>
            </div>

            {answer && (
              <div className="result-box fade-in">
                <ReactMarkdown>{answer}</ReactMarkdown>
              </div>
            )}
          </section>
        )}

      </main>

      {/* ── Footer ── */}
      <footer className="footer">
        <p>Built with FastAPI · FAISS · sentence-transformers · OpenRouter</p>
      </footer>

    </div>
  );
}

export default App;