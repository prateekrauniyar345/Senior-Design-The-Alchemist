import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';

// import hedare and footer
import Header from "./components/shared/header.jsx";
import Footer from "./components/shared/footer.jsx";
 

// import pages
import Dashboard from "./pages/Dashboard.jsx";

// import auth pages
import SignIn from "./components/auth/SignIn.jsx";
import SignUp from "./components/auth/Signup.jsx";


function App() {
  return (
    <>
      <BrowserRouter>
        {/* Header */}
        <Header />

          {/* routes */}
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/signin" element={<SignIn />} />
            <Route path="/signup" element={<SignUp />} />
          </Routes>

          {/* Footer */}
          <Footer />
      </BrowserRouter>

      
    </>
  );
}

export default App;
