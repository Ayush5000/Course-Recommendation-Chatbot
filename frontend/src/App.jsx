
import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "";

const suggestions = [
  "Learn Python from scratch",
  "Machine Learning for beginners",
  "Full Stack Web Development",
  "Data Science with Python",
];

function App() {
  const [topic, setTopic] = useState("");
  const [budget, setBudget] = useState("any");
  const [level, setLevel] = useState("any");
  const [messages, setMessages] = useState([]);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event, suggestedTopic) {
    event?.preventDefault();

    const currentTopic = (suggestedTopic || topic).trim();

    if (!currentTopic || loading) return;

    setError("");
    setLoading(true);
    setTopic("");

    const previousMessages = messages;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: currentTopic },
    ]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: currentTopic,
          budget,
          level,
          limit: 6,
          history: previousMessages.map((message) => ({
            role: message.role,
            content: message.content,
          })),
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to fetch recommendations.");
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.response,
        },
      ]);

      setCourses(data.courses || []);
    } catch (err) {
      setError(
        err.message || "Something went wrong. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function startNewChat() {
    setMessages([]);
    setCourses([]);
    setTopic("");
    setError("");
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h2>CourseAI</h2>
            <p>Learn smarter</p>
          </div>
        </div>

        <button className="new-chat" onClick={startNewChat}>
          + New recommendation
        </button>

        <div className="sidebar-bottom">
          <span className="status-dot" />
          AI Recommendation Engine
        </div>
      </aside>

      <main className="main">
        <header className="header">
          <div>
            <span className="eyebrow">YOUR LEARNING COMPANION</span>
            <h1>Discover your next skill.</h1>
            <p>
              Find courses tailored to your goals, experience
              and budget.
            </p>
          </div>
          <div className="header-badge">✦ Powered by AI</div>
        </header>

        <section className="content">
          {messages.length === 0 && (
            <div className="welcome">
              <div className="hero-icon">✦</div>
              <h2>What do you want to learn?</h2>
              <p>
                Tell us your learning goal and we'll find
                relevant courses for you.
              </p>

              <div className="suggestions">
                {suggestions.map((suggestion) => (
                  <button
                    key={suggestion}
                    onClick={() =>
                      handleSubmit(null, suggestion)
                    }
                    disabled={loading}
                  >
                    <span>↗</span>
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="messages">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`message ${message.role}`}
              >
                <div className="avatar">
                  {message.role === "user" ? "Y" : "✦"}
                </div>
                <div className="message-body">
                  <span className="message-label">
                    {message.role === "user"
                      ? "You"
                      : "CourseAI"}
                  </span>
                  <div className="message-text">
                    {message.content}
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="message assistant">
                <div className="avatar">✦</div>
                <div className="message-body">
                  <span className="message-label">
                    CourseAI
                  </span>
                  <div className="loading-text">
                    Finding relevant courses
                    <span className="dots">...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {courses.length > 0 && (
            <section className="results">
              <div className="results-heading">
                <div>
                  <span className="eyebrow">
                    CURATED FOR YOU
                  </span>
                  <h2>Recommended courses</h2>
                </div>
                <span className="count">
                  {courses.length} courses
                </span>
              </div>

              <div className="course-grid">
                {courses.map((course, index) => (
                  <article
                    className="course-card"
                    key={`${course.url}-${index}`}
                  >
                    <div className="card-top">
                      <span className="provider">
                        {course.provider}
                      </span>
                      <span
                        className={`price-tag ${
                          course.pricing
                            ?.toLowerCase()
                            .includes("free")
                            ? "free"
                            : "paid"
                        }`}
                      >
                        {course.pricing}
                      </span>
                    </div>

                    <h3>{course.title}</h3>
                    <p className="description">
                      {course.description}
                    </p>

                    <div className="course-tags">
                      <span>{course.level}</span>
                      <span>{course.category}</span>
                    </div>

                    <a
                      className="course-link"
                      href={course.url}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      View course <span>↗</span>
                    </a>
                  </article>
                ))}
              </div>
            </section>
          )}
        </section>

        <div className="composer-container">
          {error && <div className="error">{error}</div>}

          <div className="filters">
            <label>
              Budget
              <select
                value={budget}
                onChange={(e) =>
                  setBudget(e.target.value)
                }
              >
                <option value="any">All courses</option>
                <option value="free">Free</option>
                <option value="paid">Paid</option>
              </select>
            </label>

            <label>
              Skill level
              <select
                value={level}
                onChange={(e) =>
                  setLevel(e.target.value)
                }
              >
                <option value="any">All levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">
                  Intermediate
                </option>
                <option value="advanced">Advanced</option>
              </select>
            </label>
          </div>

          <form
            className="composer"
            onSubmit={handleSubmit}
          >
            <input
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="What would you like to learn?"
              disabled={loading}
            />

            <button
              type="submit"
              disabled={!topic.trim() || loading}
            >
              ↑
            </button>
          </form>

          <p className="disclaimer">
            Course prices and certificate availability
            may change. Verify details on the provider's
            website.
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;