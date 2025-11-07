import { Link } from "react-router-dom";
import "./HeaderFooter.css";

export default function Header() {
  return (
    <header className="dd-nav">
      <Link to="/" className="dd-brand" aria-label="Go to main page">
        <img
          src="/images/the-alchemist.png"
          alt=""
          className="dd-logo"
          loading="lazy"
        />
        <span className="dd-name">The Alchemist</span>
      </Link>

      <nav className="dd-actions">
        <Link to="/login" className="dd-btn dd-btn--signin">Sign In</Link>
        <Link to="/signup" className="dd-btn dd-btn--signup">Sign Up</Link>
      </nav>
    </header>
  );
}
