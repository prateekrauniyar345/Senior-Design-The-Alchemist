import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/apiClient';
import { supabase } from '../lib/supabase';

const AuthContext = createContext(null);

/** Remove Supabase and related keys so no client session survives a dev reload. */
function clearClientAuthStorage() {
  try {
    for (const store of [localStorage, sessionStorage]) {
      const toRemove = [];
      for (let i = 0; i < store.length; i++) {
        const k = store.key(i);
        if (k && (k.startsWith('sb-') || k.toLowerCase().includes('supabase'))) {
          toRemove.push(k);
        }
      }
      toRemove.forEach((k) => store.removeItem(k));
    }
  } catch {
    /* ignore */
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const bootstrap = async () => {
      // Local dev: always start logged out (no cookie / client restore). Production: /me restore.
      if (import.meta.env.DEV) {
        try {
          await apiClient.post("/api/auth/logout");
        } catch {
          /* ignore: no cookies or API down */
        }
        try {
          await supabase.auth.signOut();
        } catch {
          /* ignore */
        }
        clearClientAuthStorage();
        setUser(null);
        setLoading(false);
        return;
      }
      await checkAuth();
    };
    bootstrap();
  }, []);

  const checkAuth = async () => {
    try {
      const res = await apiClient.get("/api/auth/me");
      setUser(res.data.user);
    } catch (err) {
      // Any error during checkAuth means user is not authenticated
      // This is expected - just set user to null, don't redirect
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    const res = await apiClient.post("/api/auth/login", { email, password });
    const data = res.data;
    setUser(data.user);
    return data;
  };

  const register = async (name, email, password) => {
    const res = await apiClient.post("/api/auth/register", { name, email, password });
    if (res.data?.user) {
      setUser(res.data.user);
    }
    return res.data;
  };

  const logout = async () => {
    try {
      await apiClient.post("/api/auth/logout");
    } catch (err) {
      console.error('Logout failed:', err.message);
    }
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
