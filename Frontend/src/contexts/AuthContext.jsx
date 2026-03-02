import { createContext, useContext, useEffect, useState } from "react";
import { parseJsonOrText } from "../utils/http";
import { supabaseClient } from "../lib/supabaseClient";

const AuthContext = createContext(null);

const API = import.meta.env.VITE_API_URL;

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [booting, setBooting] = useState(true);

  async function login(email, password) {
    const res = await fetch(`${API}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ email, password }),
    });

    const data = await parseJsonOrText(res);
    setUser(data.user);
    return data;
  }

  async function register(name, email, password) {
    const res = await fetch(`${API}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ name, email, password }),
    });
    return await parseJsonOrText(res);
  }

  async function logout() {
    await fetch(`${API}/api/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    await supabaseClient.auth.signOut();
    setUser(null);
  }

  async function refreshMe() {
    const res = await fetch(`${API}/api/auth/me`, {
      method: "GET",
      credentials: "include",
    });
    const data = await parseJsonOrText(res);
    setUser(data.user);
    return data.user;
  }

  // On first mount only: mark boot complete. Do NOT set user=null or call logout.
  // User is set only after explicit login or OAuth callback. Navigation must not reset auth.
  useEffect(() => {
    setBooting(false);
  }, []);

  function setUserFromOAuth(userPayload) {
    setUser(userPayload ? { id: userPayload.id, email: userPayload.email } : null);
  }

  return (
    <AuthContext.Provider
      value={{ user, booting, login, register, logout, refreshMe, setUserFromOAuth }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
