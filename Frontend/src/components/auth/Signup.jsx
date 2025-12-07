import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useAuth } from "../../contexts/AuthContext";
import "./auth.css";

export default function SignUp() {
  const nav = useNavigate();
  const { register } = useAuth();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    const fd = new FormData(e.target);
    
    try {
      await register(
        fd.get("name"),
        fd.get("email"),
        fd.get("password")
      );
      
      // Redirect to signin page after successful registration
      nav("/signin");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
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

          <button className="primary-btn" type="submit" disabled={loading}>
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="meta">
          Already have an account? <Link to="/signin">Sign in</Link>
        </p>
        <p className="meta">
          By signing up, you agree to our <a href="/terms-of-service">Terms</a> and <a href="/privacy-policy">Privacy</a>.
        </p>

        <div className="d-flex justify-content-center align-item-center">
          {/* Back to Home */}
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
