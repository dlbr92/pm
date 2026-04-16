import json

from pydantic import ValidationError

from app.schemas.ai_chat import AIChatHistoryItem, AIChatModelOutput
from app.schemas.board import BoardModel
from app.services.ai_service import AIService, AIServiceError
from app.services.board_service import BoardService


AI_CHAT_SYSTEM_PROMPT = """
You are an assistant for a Kanban board app.
Return ONLY valid JSON and no markdown.
The JSON object must match this exact schema:
{
  "reply": "string",
  "board_update": null | {
    "columns": [{"id":"string","title":"string","cardIds":["string"]}],
    "cards": {"card-id":{"id":"string","title":"string","details":"string"}}
  }
}
Rules:
- "reply" is required.
- "board_update" can be null.
- If "board_update" is provided, it must be a full valid board object.
""".strip()


class AIChatService:
    def __init__(self, ai_service: AIService, board_service: BoardService):
        self.ai_service = ai_service
        self.board_service = board_service

    @staticmethod
    def parse_model_output(raw_output: str) -> AIChatModelOutput:
        try:
            payload = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise AIServiceError("AI returned malformed JSON.", status_code=502) from exc

        try:
            return AIChatModelOutput.model_validate(payload)
        except ValidationError as exc:
            raise AIServiceError(
                "AI JSON did not match required schema.",
                status_code=502,
            ) from exc

    def run(
        self,
        message: str,
        history: list[AIChatHistoryItem],
    ) -> tuple[str, BoardModel, bool]:
        current_board = self.board_service.get_board()
        prompt_payload = {
            "current_board": current_board.model_dump(mode="json"),
            "history": [item.model_dump(mode="json") for item in history],
            "message": message,
        }
        raw_output = self.ai_service.complete_messages(
            [
                {"role": "system", "content": AI_CHAT_SYSTEM_PROMPT},
                {"role": "user", "content": json.dumps(prompt_payload)},
            ]
        )
        parsed_output = self.parse_model_output(raw_output)

        if parsed_output.board_update is None:
            return parsed_output.reply, current_board, False

        updated_board = self.board_service.update_board(parsed_output.board_update)
        return parsed_output.reply, updated_board, True
