import { Container } from "react-bootstrap";

export default function Home() {
  return (
    <Container
      fluid
      className="px-0 d-flex flex-column min-vh-100 justify-content-center align-items-center text-white"
    >
      <h1>Welcome to The Alchemist</h1>
      <p>This is the home page.</p>
    </Container>
  );
}
