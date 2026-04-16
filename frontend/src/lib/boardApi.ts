import type { BoardData } from "@/lib/kanban";

const BOARD_ENDPOINT = "/api/board";

const parseBoardResponse = async (response: Response): Promise<BoardData> => {
  if (!response.ok) {
    throw new Error(`Board request failed with status ${response.status}.`);
  }
  return (await response.json()) as BoardData;
};

export const fetchBoard = async (): Promise<BoardData> => {
  const response = await fetch(BOARD_ENDPOINT, { method: "GET" });
  return parseBoardResponse(response);
};

export const saveBoard = async (board: BoardData): Promise<BoardData> => {
  const response = await fetch(BOARD_ENDPOINT, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(board),
  });
  return parseBoardResponse(response);
};
