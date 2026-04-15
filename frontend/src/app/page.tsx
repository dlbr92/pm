"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { AUTH_STORAGE_KEY, isValidCredentials } from "@/lib/auth";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const existingSession = window.sessionStorage.getItem(AUTH_STORAGE_KEY);
    setIsAuthenticated(existingSession === "true");
  }, []);

  const handleLogin = (username: string, password: string) => {
    const isValid = isValidCredentials(username, password);
    if (!isValid) {
      return false;
    }
    window.sessionStorage.setItem(AUTH_STORAGE_KEY, "true");
    setIsAuthenticated(true);
    return true;
  };

  const handleLogout = () => {
    window.sessionStorage.removeItem(AUTH_STORAGE_KEY);
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  return <KanbanBoard onLogout={handleLogout} />;
}
