import { Container, Nav } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer role="contentinfo" className="border-top mt-auto">
      <Container fluid className="px-5 py-4">
        {/* First line: full-width links */}
        <div className="w-100">
          <Nav className="justify-content-center">
            <Nav.Link as={Link} to="/about" className="px-3 text-light">
              About Us
            </Nav.Link>
            <Nav.Link as={Link} to="/privacy-policy" className="px-3 text-light">
              Privacy Policy
            </Nav.Link>
            <Nav.Link as={Link} to="/terms-of-service" className="px-3 text-light">
              Terms of Service
            </Nav.Link>
          </Nav>
        </div>

        {/* Second line: full-width copyright */}
        <div className="w-100 text-center text-secondary mt-2 small">
          © 2025 The Alchemist. All rights reserved.
        </div>
      </Container>
    </footer>
  );
}