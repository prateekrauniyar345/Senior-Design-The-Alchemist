import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
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
