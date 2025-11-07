import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';

import Footer from "./components/shared/footer.jsx";
 
import Dashboard from "./pages/Dashboard.jsx";
import SignIn from "./components/auth/SignIn.jsx";
import SignUp from "./components/auth/Signup.jsx";
import Chat from "./pages/Chat.jsx";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/chat" element={<Chat />} /> {/* No footer here */}
      </Routes>

      {/* Only show footer on non-chat routes */}
      <Routes>
        <Route path="/" element={<Footer />} />
        <Route path="/signin" element={null} />
        <Route path="/signup" element={null} />
        <Route path="/chat" element={null} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;