import { Routes, Route, useLocation } from "react-router-dom";
import "./App.css";

import Footer from "./components/shared/footer.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Login from "./pages/Login.jsx";
import AuthCallback from "./pages/AuthCallback.jsx";
import SignUp from "./components/auth/Signup.jsx";
import ChatPage from "./pages/Chat.jsx";
import Logout from "./pages/Logout.jsx";

// No key on AppLayout or Routes — keys that change with location would remount the tree and wipe auth state.
function AppLayout() {
  const location = useLocation();
  const hideFooter = location.pathname.startsWith("/chat");

  return (
    <>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/signin" element={<Login />} />
        <Route path="/login" element={<Login />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/logout" element={<Logout />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/chat" element={<ChatPage />} />
        </Route>
      </Routes>

      {!hideFooter && <Footer />}
    </>
  );
}

export default function App() {
  return <AppLayout />;
}
