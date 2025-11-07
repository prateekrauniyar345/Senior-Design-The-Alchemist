import { Container } from "react-bootstrap";
import { testBackendHealth } from "../api/testEndpoint";
import { useState, useEffect } from "react";

export default function Dashboard() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    async function fetchBackendHealth() {
      const data = await testBackendHealth();
      setHealth(data);
    }
    fetchBackendHealth();
  }, []);

  return (
    <Container
      fluid
      className="px-0 d-flex flex-column min-vh-100 justify-content-center align-items-center text-white"
    >
      <h1>Welcome to The Alchemist</h1>
      <p className="mt-3">{health ? JSON.stringify(health) : "Checking backend health..."}</p>
    </Container>
  );
}