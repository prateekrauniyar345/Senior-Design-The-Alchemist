import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./auth.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function Login() {
  const nav = useNavigate();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

async function handleSubmit(e) {
  e.preventDefault();
  setError("");
  setLoading(true);

  const fd = new FormData(e.target);
  const payload = {
    email: fd.get("email"),
    password: fd.get("password"),
  };

  try {
    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",     // crucial for cookies
      body: JSON.stringify(payload),
    });

    const data = await res.json().catch(() => ({}));
    if (res.ok) {
  // Full page redirect to FastAPI dashboard
  window.location.href = `${API_URL}/dashboard`;
}


    // 🔁 Jump to the backend dashboard (full page load on :8000)
    window.location.href = `${API_URL}/dashboard`;
  } catch (err) {
    setError(err.message || "Login failed");
  } finally {
    setLoading(false);
  }
}


  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h2>Sign in to your account</h2>
        <p className="auth-sub">Enter your credentials to continue</p>

        {error && <div className="error">{error}</div>}

        <button
          className="microsoft-btn"
          onClick={() => alert("Hook up MS OAuth later")}
          type="button"
        >
          Continue with Microsoft
        </button>
        <p className="divider">Or continue with email</p>

        <form className="form" onSubmit={handleSubmit}>
          <label className="label">Email</label>
          <input
            className="input"
            name="email"
            type="email"
            placeholder="name@example.com"
            required
          />

          <label className="label">Password</label>
          <input
            className="input"
            name="password"
            type="password"
            placeholder="••••••••"
            required
          />

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <p className="meta">
          Don’t have an account? <Link to="/signup">Sign up</Link>
        </p>
        <p className="meta">
          By signing in, you agree to our <a href="/terms-of-service">Terms</a> and{" "}
          <a href="/privacy-policy">Privacy</a>.
        </p>
      </div>
    </div>
  );
}
