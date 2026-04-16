"use client";

import { useState, type FormEvent } from "react";
import type { AIChatHistoryItem } from "@/lib/aiChatApi";

type AIChatSidebarProps = {
  messages: AIChatHistoryItem[];
  isLoading: boolean;
  error: string | null;
  onSend: (message: string) => Promise<void>;
};

export const AIChatSidebar = ({
  messages,
  isLoading,
  error,
  onSend,
}: AIChatSidebarProps) => {
  const [draft, setDraft] = useState("");

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || isLoading) {
      return;
    }
    setDraft("");
    await onSend(trimmed);
  };

  return (
    <aside className="flex h-full min-h-[420px] flex-col rounded-3xl border border-[var(--stroke)] bg-white/95 p-4 shadow-[var(--shadow)] backdrop-blur">
      <h2 className="font-display text-xl font-semibold text-[var(--navy-dark)]">
        AI Assistant
      </h2>
      <p className="mt-1 text-xs uppercase tracking-[0.2em] text-[var(--gray-text)]">
        Ask to create, edit, or move cards
      </p>

      <div
        className="mt-4 flex min-h-[260px] flex-1 flex-col gap-3 overflow-y-auto rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-3"
        data-testid="ai-chat-history"
      >
        {messages.length === 0 ? (
          <p className="text-sm text-[var(--gray-text)]">
            No messages yet. Try: &quot;Move card-1 to Review&quot;.
          </p>
        ) : null}
        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}`}
            className={
              message.role === "user"
                ? "self-end rounded-2xl bg-[var(--primary-blue)] px-3 py-2 text-sm text-white"
                : "self-start rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)]"
            }
          >
            {message.content}
          </div>
        ))}
        {isLoading ? (
          <p className="self-start text-xs text-[var(--gray-text)]">Thinking...</p>
        ) : null}
      </div>

      {error ? (
        <p role="alert" className="mt-3 text-sm text-[#b3261e]">
          {error}
        </p>
      ) : null}

      <form className="mt-3 flex flex-col gap-2" onSubmit={handleSubmit}>
        <textarea
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Ask AI to update the board..."
          className="h-24 w-full resize-none rounded-2xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--secondary-purple)]"
          aria-label="AI message"
        />
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-70"
        >
          Send
        </button>
      </form>
    </aside>
  );
};
