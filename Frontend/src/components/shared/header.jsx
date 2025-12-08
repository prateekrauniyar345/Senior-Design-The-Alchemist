import { Navbar, Nav, Button, Dropdown } from "react-bootstrap";
import { LogIn, UserPlus, User, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/logout');
  };

  return(
      <Navbar variant="dark" expand="lg" className="py-3">
        <Navbar.Brand href="/" className="d-flex align-items-center text-white">
            <span className="fw-bold" style={{ fontSize: '2.1rem' }}>The Alchemist</span>
        </Navbar.Brand>
        
        <Navbar.Toggle aria-controls="nav" />
        <Navbar.Collapse id="nav">
            <Nav className="ms-auto me-3 d-none d-lg-flex fs-4">
                <Nav.Link href="/" className="text-white px-3">Dashboard</Nav.Link>
                <Nav.Link href="/chat" className="text-secondary px-3">Chat</Nav.Link>
                <Nav.Link href="/docs" className="text-secondary px-3">Docs</Nav.Link>
            </Nav>
            
            <div className="d-flex align-items-center gap-4 mt-3 mt-lg-0">
              {user ? (
                // Show user info when logged in
                <Dropdown align="end">
                  <Dropdown.Toggle variant="outline-light" className="d-flex align-items-center gap-2">
                    <User size={20} />
                    <span>{user.name || user.email}</span>
                  </Dropdown.Toggle>
                  <Dropdown.Menu>
                    <Dropdown.Item onClick={handleLogout}>
                      <LogOut size={16} className="me-2" />
                      Logout
                    </Dropdown.Item>
                  </Dropdown.Menu>
                </Dropdown>
              ) : (
                // Show login/signup buttons when not logged in
                <>
                  <Nav.Link href="/signin" className="text-white px-3">
                      <Button variant="link" className="text-white text-decoration-none p-0 d-flex align-items-center fs-5">
                          <LogIn size={22} className="me-2" />
                          <span>Sign In</span>
                      </Button>
                  </Nav.Link>

                  <Nav.Link href="/signup" className="text-white px-3">
                    <Button 
                        variant="outline-light" 
                        size="lg"
                        className="d-flex align-items-center fs-5"
                    >
                        <UserPlus size={22} className="me-2" />
                        Sign Up
                    </Button>
                  </Nav.Link>
                </>
              )}
            </div>
        </Navbar.Collapse>
    </Navbar>
  );
}