import json

import pytest

from app.schemas.ai_chat import AIChatHistoryItem
from app.schemas.board import BoardModel, CardModel, ColumnModel
from app.services.ai_chat_service import AIChatService
from app.services.ai_service import AIServiceError


class FakeAIService:
    def __init__(self, output: str):
        self.output = output
        self.messages: list[dict[str, str]] | None = None

    def complete_messages(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        return self.output


class FakeBoardService:
    def __init__(self, board: BoardModel):
        self.board = board
        self.update_calls = 0

    def get_board(self) -> BoardModel:
        return self.board

    def update_board(self, board: BoardModel) -> BoardModel:
        self.update_calls += 1
        self.board = board
        return board


def make_board() -> BoardModel:
    return BoardModel(
        columns=[ColumnModel(id="col-1", title="Col 1", cardIds=["card-1"])],
        cards={"card-1": CardModel(id="card-1", title="Card 1", details="Details")},
    )


def test_parser_rejects_non_json() -> None:
    with pytest.raises(AIServiceError) as exc:
        AIChatService.parse_model_output("not-json")
    assert exc.value.status_code == 502


def test_parser_rejects_invalid_schema() -> None:
    with pytest.raises(AIServiceError) as exc:
        AIChatService.parse_model_output(json.dumps({"reply": ""}))
    assert exc.value.status_code == 502


def test_run_passes_board_history_and_message_to_model() -> None:
    model_output = json.dumps({"reply": "ok", "board_update": None})
    fake_ai = FakeAIService(output=model_output)
    fake_board = FakeBoardService(board=make_board())
    service = AIChatService(ai_service=fake_ai, board_service=fake_board)

    reply, _board, board_updated = service.run(
        message="Please summarize.",
        history=[AIChatHistoryItem(role="user", content="Earlier message.")],
    )

    assert reply == "ok"
    assert board_updated is False
    assert fake_ai.messages is not None
    assert len(fake_ai.messages) == 2
    prompt_payload = json.loads(fake_ai.messages[1]["content"])
    assert prompt_payload["message"] == "Please summarize."
    assert prompt_payload["history"][0]["content"] == "Earlier message."
    assert "columns" in prompt_payload["current_board"]
