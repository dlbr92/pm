import json

from fastapi.testclient import TestClient

from app.main import app, get_ai_service


class FakeAIService:
    model = "gpt-4.1-mini"

    def __init__(self, model_output: str):
        self.model_output = model_output

    def complete_messages(self, _messages: list[dict[str, str]]) -> str:
        return self.model_output


def build_board_payload(column_title: str) -> dict:
    return {
        "columns": [
            {"id": "col-backlog", "title": column_title, "cardIds": ["card-1"]},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-1": {
                "id": "card-1",
                "title": "Card one",
                "details": "Card details",
            }
        },
    }


def test_ai_chat_response_only_does_not_update_board(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "chat-response-only.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(
        model_output=json.dumps({"reply": "No board change.", "board_update": None})
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/ai/chat",
                json={"message": "What should I do next?", "history": []},
            )
            assert response.status_code == 200
            payload = response.json()
            assert payload["reply"] == "No board change."
            assert payload["boardUpdated"] is False
    finally:
        app.dependency_overrides.clear()


def test_ai_chat_response_with_board_update_persists(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "chat-board-update.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    updated_board = build_board_payload("AI Backlog")
    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(
        model_output=json.dumps({"reply": "Updated board.", "board_update": updated_board})
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/ai/chat",
                json={"message": "Rename backlog to AI Backlog", "history": []},
            )
            assert response.status_code == 200
            payload = response.json()
            assert payload["boardUpdated"] is True
            assert payload["board"]["columns"][0]["title"] == "AI Backlog"

            current_board = client.get("/api/board")
            assert current_board.status_code == 200
            assert current_board.json()["columns"][0]["title"] == "AI Backlog"
    finally:
        app.dependency_overrides.clear()


def test_ai_chat_rejects_malformed_model_output_and_keeps_board(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "chat-malformed.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    with TestClient(app) as client:
        seed_board = build_board_payload("Seed Backlog")
        seed_response = client.put("/api/board", json=seed_board)
        assert seed_response.status_code == 200

    app.dependency_overrides[get_ai_service] = lambda: FakeAIService(
        model_output="this is not json"
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/ai/chat",
                json={"message": "Try malformed update", "history": []},
            )
            assert response.status_code == 502

            current_board = client.get("/api/board")
            assert current_board.status_code == 200
            assert current_board.json()["columns"][0]["title"] == "Seed Backlog"
    finally:
        app.dependency_overrides.clear()
