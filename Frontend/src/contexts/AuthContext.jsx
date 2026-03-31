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

  // Bootstrap auth on app load: restore user from session cookie via /me.
  // Keeps booting=true until the request completes so ProtectedRoute does not redirect prematurely.
  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const res = await fetch(`${API}/api/auth/me`, {
          method: "GET",
          credentials: "include",
        });
        if (cancelled) return;
        const data = await parseJsonOrText(res);
        setUser(data.user);
      } catch {
        // 401 or network error: no valid session, leave user null
        if (!cancelled) setUser(null);
      } finally {
        if (!cancelled) setBooting(false);
      }
    }

    bootstrap();
    return () => { cancelled = true; };
  }, []);

  function setUserFromOAuth(userPayload) {
    if (!userPayload) {
      setUser(null);
      return;
    }
    const meta = userPayload.user_metadata || {};
    const name = (meta.name || meta.full_name || "").trim();
    setUser({ id: userPayload.id, email: userPayload.email, name });
  }

  function updateUser(partial) {
    setUser((prev) => (prev ? { ...prev, ...partial } : null));
  }

  return (
    <AuthContext.Provider
      value={{ user, booting, login, register, logout, refreshMe, setUserFromOAuth, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
