import type { BoardData } from "@/lib/kanban";

export type AIChatHistoryItem = {
  role: "user" | "assistant";
  content: string;
};

export type AIChatResponse = {
  reply: string;
  boardUpdated: boolean;
  board: BoardData;
};

const AI_CHAT_ENDPOINT = "/api/ai/chat";

export const sendAIChat = async (
  message: string,
  history: AIChatHistoryItem[]
): Promise<AIChatResponse> => {
  const response = await fetch(AI_CHAT_ENDPOINT, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`AI chat request failed with status ${response.status}.`);
  }

  return (await response.json()) as AIChatResponse;
};
