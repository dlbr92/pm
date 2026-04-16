"use client";

import { useEffect, useState } from "react";
import { AIChatSidebar } from "@/components/AIChatSidebar";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { sendAIChat, type AIChatHistoryItem } from "@/lib/aiChatApi";
import { AUTH_STORAGE_KEY, isValidCredentials } from "@/lib/auth";
import { fetchBoard, saveBoard } from "@/lib/boardApi";
import type { BoardData } from "@/lib/kanban";

export default function Home() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [board, setBoard] = useState<BoardData | null>(null);
  const [isBoardLoading, setIsBoardLoading] = useState(false);
  const [boardLoadError, setBoardLoadError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [boardSaveError, setBoardSaveError] = useState<string | null>(null);
  const [boardReloadCount, setBoardReloadCount] = useState(0);
  const [chatMessages, setChatMessages] = useState<AIChatHistoryItem[]>([]);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const [chatError, setChatError] = useState<string | null>(null);

  useEffect(() => {
    const existingSession = window.sessionStorage.getItem(AUTH_STORAGE_KEY);
    setIsAuthenticated(existingSession === "true");
  }, []);

  useEffect(() => {
    if (!isAuthenticated) {
      setBoard(null);
      return;
    }

    const loadBoard = async () => {
      setIsBoardLoading(true);
      setBoardLoadError(null);
      try {
        const nextBoard = await fetchBoard();
        setBoard(nextBoard);
      } catch {
        setBoardLoadError("Unable to load your board. Please try again.");
      } finally {
        setIsBoardLoading(false);
      }
    };

    void loadBoard();
  }, [isAuthenticated, boardReloadCount]);

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
    setBoard(null);
    setBoardLoadError(null);
    setBoardSaveError(null);
    setIsSaving(false);
    setChatMessages([]);
    setChatError(null);
    setIsChatLoading(false);
  };

  const handleBoardChange = (nextBoard: BoardData) => {
    setBoard(nextBoard);
    setBoardSaveError(null);
    setIsSaving(true);
    void saveBoard(nextBoard)
      .then((persistedBoard) => {
        setBoard(persistedBoard);
      })
      .catch(() => {
        setBoardSaveError("Unable to save board changes.");
      })
      .finally(() => {
        setIsSaving(false);
      });
  };

  const handleSendAIMessage = async (message: string) => {
    const history = [...chatMessages];
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatError(null);
    setIsChatLoading(true);
    try {
      const response = await sendAIChat(message, history);
      setChatMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.reply },
      ]);
      setBoard(response.board);
    } catch {
      setChatError("Unable to get AI response right now.");
    } finally {
      setIsChatLoading(false);
    }
  };

  if (!isAuthenticated) {
    return <LoginForm onLogin={handleLogin} />;
  }

  if (boardLoadError && !board) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <div className="max-w-md rounded-2xl border border-[var(--stroke)] bg-white px-6 py-5 text-sm shadow-[var(--shadow)]">
          <p className="text-[#b3261e]">{boardLoadError}</p>
          <button
            type="button"
            onClick={() => setBoardReloadCount((prev) => prev + 1)}
            className="mt-4 rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </main>
    );
  }

  if (isBoardLoading || !board) {
    return (
      <main className="flex min-h-screen items-center justify-center p-8">
        <div className="rounded-2xl border border-[var(--stroke)] bg-white px-6 py-4 text-sm text-[var(--gray-text)] shadow-[var(--shadow)]">
          Loading board...
        </div>
      </main>
    );
  }

  return (
    <KanbanBoard
      board={board}
      onBoardChange={handleBoardChange}
      onLogout={handleLogout}
      isSaving={isSaving}
      saveError={boardSaveError}
      sidebar={
        <AIChatSidebar
          messages={chatMessages}
          isLoading={isChatLoading}
          error={chatError}
          onSend={handleSendAIMessage}
        />
      }
    />
  );
}
