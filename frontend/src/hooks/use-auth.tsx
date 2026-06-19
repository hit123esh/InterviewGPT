"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authService } from "@/services/auth.service";
import type { User } from "@/types/auth";

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      if (authService.isAuthenticated()) {
        const me = await authService.getMe();
        setUser(me);
      }
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  async function login(email: string, password: string) {
    await authService.login({ email, password });
    const me = await authService.getMe();
    setUser(me);
  }

  async function register(email: string, password: string, fullName: string) {
    await authService.register({ email, password, full_name: fullName });
    await login(email, password);
  }

  function logout() {
    setUser(null);
    authService.logout();
  }

  return (
    <AuthContext.Provider
      value={{ user, loading, login, register, logout, isAuthenticated: !!user }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
