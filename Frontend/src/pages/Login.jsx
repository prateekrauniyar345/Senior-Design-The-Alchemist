import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useAuth } from "../contexts/AuthContext";
import { supabaseClient } from "../lib/supabaseClient";
import "../components/auth/auth.css";

const redirectTo = `${window.location.origin}/auth/callback`;

export default function Login() {
  const nav = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(null); // "google" | "azure" | null

  /** Email/password login via FastAPI; backend sets cookies. */
  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const fd = new FormData(e.target);

    try {
      await login(fd.get("email"), fd.get("password"));
      nav("/chat");
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  /** OAuth: redirect to Supabase, then Supabase redirects to /auth/callback. Session is in memory only (persistSession: false). */
  async function handleOAuth(provider) {
    setError("");
    setOauthLoading(provider);

    try {
      const { error: oauthError } = await supabaseClient.auth.signInWithOAuth({
        provider,
        options: { redirectTo },
      });
      if (oauthError) {
        setError(oauthError.message || "OAuth failed");
        setOauthLoading(null);
      }
      // Else: browser redirects away; no need to set loading false
    } catch (err) {
      setError(err.message || "OAuth failed");
      setOauthLoading(null);
    }
  }

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h2>Sign in to your account</h2>
        <p className="auth-sub">Enter your credentials or continue with a provider</p>

        {error && <div className="error">{error}</div>}

        <button
          className="oauth-btn google-btn"
          type="button"
          disabled={!!oauthLoading}
          onClick={() => handleOAuth("google")}
        >
          {oauthLoading === "google" ? "Redirecting…" : "Continue with Google"}
        </button>
        <button
          className="oauth-btn microsoft-btn"
          type="button"
          disabled={!!oauthLoading}
          onClick={() => handleOAuth("azure")}
        >
          {oauthLoading === "azure" ? "Redirecting…" : "Continue with Microsoft"}
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
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <p className="meta">
          Don&apos;t have an account? <Link to="/signup">Sign up</Link>
        </p>
        <p className="meta">
          By signing in, you agree to our <a href="/terms-of-service">Terms</a> and{" "}
          <a href="/privacy-policy">Privacy</a>.
        </p>

        <div className="d-flex justify-content-center align-item-center">
          <button
            onClick={() => nav("/")}
            className="btn btn-link text-light d-flex align-items-center gap-2 mt-3"
            style={{ textDecoration: "none" }}
            aria-label="Back to home"
          >
            <ArrowLeft size={18} />
            <span>Go home</span>
          </button>
        </div>
      </div>
    </div>
  );
}
