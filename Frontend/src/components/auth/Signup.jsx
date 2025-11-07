import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./auth.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function SignUp() {
  const nav = useNavigate();
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    const fd = new FormData(e.target); // name, email, password
    try {
      const res = await fetch(`${API_URL}/register`, {
        method: "POST",
        body: fd,
        credentials: "include",
      });
      if (res.redirected || res.ok) {
        nav("/login");
      } else {
        setError(await res.text());
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h2>Create an account</h2>
        <p className="auth-sub">Enter your details to get started</p>

        {error && <div className="error">{error}</div>}

        <button className="microsoft-btn" onClick={() => alert("Hook up MS OAuth later")}>
          Continue with Microsoft
        </button>
        <p className="divider">Or continue with email</p>

        <form className="form" onSubmit={handleSubmit}>
          <label className="label">Full name</label>
          <input className="input" name="name" type="text" placeholder="Alex Doe" required />

          <label className="label">Email</label>
          <input className="input" name="email" type="email" placeholder="name@example.com" required />

          <label className="label">Password</label>
          <input className="input" name="password" type="password" placeholder="••••••••" required />

          <button className="primary-btn" type="submit">Create account</button>
        </form>

        <p className="meta">
          Already have an account? <Link to="/signin">Sign in</Link>
        </p>
        <p className="meta">
          By signing up, you agree to our <a href="/terms-of-service">Terms</a> and <a href="/privacy-policy">Privacy</a>.
        </p>
      </div>
    </div>
  );
}
