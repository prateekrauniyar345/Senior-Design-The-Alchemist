import { Navbar, Nav, Container, Button, Image } from "react-bootstrap";
import { Link } from "react-router-dom";

export default function Header() {
  return (
    <Navbar className="ms-0 me-0">
      <Container fluid className="px-5">  
        <Navbar.Brand as={Link} to="/" className="d-flex align-items-center cursor-pointer">
          <Image
            src="/images/the-alchemist.png" 
            alt="The Alchemist Logo"
            roundedCircle
            width={32}
            height={32}
            className="me-2"
          />
          <span className="fw-semibold text-white fs-1">The Alchemist</span>
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="main-nav" />
        <Navbar.Collapse id="main-nav">
          <Nav className="ms-auto align-items-lg-center">
            <Button as={Link} to="/signin" variant="outline-light" size="lg" className="me-2">
              Sign In
            </Button>
            <Button as={Link} to="/signup" variant="primary" size="lg">
              Sign Up
            </Button>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}