import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';

import Footer from "./components/shared/footer.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";
 
import Dashboard from "./pages/Dashboard.jsx";
import SignIn from "./components/auth/SignIn.jsx";
import SignUp from "./components/auth/Signup.jsx";
import Chat from "./pages/Chat.jsx";
import Logout from "./pages/Logout.jsx";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/chat" element={<Chat />} /> {/* No footer here */}
        <Route path="/logout" element={<Logout />} />
      </Routes>

      {/* Only show footer on non-chat routes */}
      <Routes>
        <Route path="/" element={<Footer />} />
        <Route path="/signin" element={null} />
        <Route path="/signup" element={null} />
        <Route path="/chat" element={null} />
        <Route path="/logout" element={null} />
      </Routes>
    </BrowserRouter>
    </AuthProvider>
  );
}

export default App;