import { BrowserRouter, Routes, Route } from "react-router-dom";
import './App.css';

// import hedare and footer
import Header from "./components/shared/header.jsx";
import Footer from "./components/shared/footer.jsx";
 

// import pages
import Home from "./pages/Home";
function App() {
  return (
    <>
      <BrowserRouter>
        {/* Header */}
        <Header />

          {/* routes */}
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>

          {/* Footer */}
          <Footer />
      </BrowserRouter>

      
    </>
  );
}

export default App;
