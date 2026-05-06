import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);

      const response = await axios.post(
        "http://127.0.0.1:8000/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setSummary(response.data.summary);
      setAnswer("");
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    }

    setLoading(false);
  };

  const askQuestion = async () => {
    if (!question) {
      alert("Enter a question");
      return;
    }

    try {
      setLoading(true);

      const response = await axios.post(
        `http://127.0.0.1:8000/ask?question=${question}`
      );

      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
      alert("Question failed");
    }

    setLoading(false);
  };

  return (
    <div className="container">
      <h1>Legal AI Assistant</h1>

      <div className="card">
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
        />

        <button onClick={handleUpload}>
          Upload PDF
        </button>
      </div>
      
      {loading && <p>Loading...</p>}
      {summary && (
        <div className="card">
          <h2>Summary</h2>
          <p>{summary}</p>
        </div>
      )}
      <div className="card">
        <h2>Ask a Question</h2>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question here"
        />
        <button onClick={askQuestion}>
          Ask
        </button>
      </div>
      {answer && (
        <div className="card">
          <h2>Answer</h2>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default App;