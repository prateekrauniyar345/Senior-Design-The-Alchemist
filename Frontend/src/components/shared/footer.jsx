import { Container, Nav , Row, Col} from "react-bootstrap";
import { Link } from "react-router-dom";

export default function Footer() {
  return (
      <footer className="py-5 mt-5" style={{ borderColor: '#1a1a1a' }}>
        <Container fluid className="px-5">
            <Row className="g-4">
                <Col md={6}>
                    <h3 className="fw-bold text-white mb-3" style={{ fontSize: '1.8rem' }}>
                        The Alchemist
                    </h3>
                    <p className="text-secondary fs-5" style={{ maxWidth: '400px' }}>
                        AI-powered mineral data exploration platform built with LangChain and LangGraph.
                    </p>
                </Col>
                <Col md={3}>
                    <h4 className="text-white mb-3 fs-5">Product</h4>
                    <Nav className="flex-column">
                        <Nav.Link href="/dashboard" className="text-secondary px-0 py-2 fs-5">Dashboard</Nav.Link>
                        <Nav.Link href="/chat" className="text-secondary px-0 py-2 fs-5">Query Agents</Nav.Link>
                        <Nav.Link href="#" className="text-secondary px-0 py-2 fs-5">API Docs</Nav.Link>
                    </Nav>
                </Col>
                <Col md={3}>
                    <h4 className="text-white mb-3 fs-5">Company</h4>
                    <Nav className="flex-column">
                        <Nav.Link href="/about" className="text-secondary px-0 py-2 fs-5">About Us</Nav.Link>
                        <Nav.Link href="/privacy-policy" className="text-secondary px-0 py-2 fs-5">Privacy Policy</Nav.Link>
                        <Nav.Link href="/terms-of-service" className="text-secondary px-0 py-2 fs-5">Terms of Service</Nav.Link>
                    </Nav>
                </Col>
            </Row>
            <hr className="my-4" style={{ borderColor: '#1a1a1a' }} />
            <div className="text-center text-secondary fs-5">
                © 2025 The Alchemist. All rights reserved.
            </div>
        </Container>
    </footer>
  );
}