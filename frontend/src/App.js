import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [topic, setTopic] = useState("");
  const [blog, setBlog] = useState("");
  const [loading, setLoading] = useState(false);

  const generateBlog = async () => {
    if (!topic) {
      alert("Please enter a topic!");
      return;
    }

    setLoading(true);
    setBlog(""); // Clear previous result

    try {
      const response = await axios.post("https://your-backend-url.com/generate", { topic });
      setBlog(response.data.blog);
    } catch (error) {
      setBlog("Error generating blog. Please try again.");
    }

    setLoading(false);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Blog Generator 🚀</h1>
        <p>Enter a topic and let AI generate a blog for you!</p>

        <input
          type="text"
          placeholder="Enter blog topic..."
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
        />

        <button onClick={generateBlog} disabled={loading}>
          {loading ? "Generating..." : "Generate Blog"}
        </button>

        {blog && (
          <div className="blog-output">
            <h2>Generated Blog</h2>
            <p>{blog}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
