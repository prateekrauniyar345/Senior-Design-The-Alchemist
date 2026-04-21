// Frontend/src/contexts/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/apiClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * Check authentication status by calling /api/auth/me endpoint.
   * This validates the session cookie and returns user info if authenticated.
   */
  const checkAuth = async () => {
    try {
      const res = await apiClient.get("/api/auth/me");
      setUser(res.data.user);
      console.log('User authenticated:', res.data.user.email);
    } catch (err) {
      // Any error during checkAuth means user is not authenticated
      // This is expected - just set user to null, don't redirect
      setUser(null);
      console.debug('User not authenticated');
    } finally {
      setLoading(false);
    }
  };

  /**
   * Initial auth check on mount
   */
  useEffect(() => {
    checkAuth();
  }, []);

  /**
   * Login with email and password.
   * Sets user state on success.
   */
  const login = async (email, password) => {
    try {
      const res = await apiClient.post("/api/auth/login", { email, password });
      const userData = res.data.user;
      setUser(userData);
      console.log('User logged in:', userData.email);
      return res.data;
    } catch (err) {
      setUser(null);
      throw err;
    }
  };

  /**
   * Register new user with name, email, and password.
   * Sets user state on success.
   */
  const register = async (name, email, password) => {
    try {
      const res = await apiClient.post("/api/auth/register", { name, email, password });
      
      // If registration was successful and we got user data, set it
      if (res.data.user) {
        setUser(res.data.user);
        console.log('User registered:', res.data.user.email);
      }
      
      return res.data;
    } catch (err) {
      setUser(null);
      throw err;
    }
  };

  /**
   * Logout the user.
   * Clears session cookies on backend and user state.
   */
  const logout = async () => {
    try {
      await apiClient.post("/api/auth/logout");
      console.log('User logged out');
    } catch (err) {
      console.error('Logout failed:', err.message);
    } finally {
      setUser(null);
    }
  };

  /**
   * Force refresh of user data from /api/auth/me
   * Useful after updating user profile
   */
  const refreshUser = async () => {
    await checkAuth();
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading, refreshUser, checkAuth }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
}
