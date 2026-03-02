import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext.jsx";
import App from "./App.jsx";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "./index.css";

// AuthProvider must mount once at the root and never unmount on route change or StrictMode.
// Order: AuthProvider > BrowserRouter > StrictMode > App. So when StrictMode double-mounts in dev,
// only App (and below) remounts; AuthProvider keeps state. Navigation never wipes auth.
ReactDOM.createRoot(document.getElementById("root")).render(
  <AuthProvider>
    <BrowserRouter>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </BrowserRouter>
  </AuthProvider>
);
