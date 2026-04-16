from fastapi.testclient import TestClient

from app.main import app


def test_get_board_returns_default_board_for_mvp_user(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "api-default.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    with TestClient(app) as client:
        response = client.get("/api/board")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["columns"]) == 5
    assert payload["cards"]["card-1"]["title"] == "Align roadmap themes"


def test_put_board_persists_updated_board(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "api-update.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    next_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"]},
            {"id": "col-done", "title": "Done", "cardIds": []},
        ],
        "cards": {
            "card-1": {
                "id": "card-1",
                "title": "Updated card",
                "details": "Persist this content",
            }
        },
    }

    with TestClient(app) as client:
        put_response = client.put("/api/board", json=next_board)
        assert put_response.status_code == 200
        assert put_response.json()["cards"]["card-1"]["title"] == "Updated card"

        get_response = client.get("/api/board")
        assert get_response.status_code == 200
        assert get_response.json()["cards"]["card-1"]["details"] == "Persist this content"


def test_put_board_rejects_invalid_payload(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "api-invalid.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    invalid_board = {
        "columns": [
            {"id": "col-backlog", "title": "Backlog", "cardIds": ["missing-card"]}
        ],
        "cards": {},
    }

    with TestClient(app) as client:
        response = client.put("/api/board", json=invalid_board)

    assert response.status_code == 422


def test_board_persists_across_testclient_restart(tmp_path, monkeypatch) -> None:
    db_path = tmp_path / "api-restart.db"
    monkeypatch.setenv("PM_DB_PATH", str(db_path))

    next_board = {
        "columns": [{"id": "col-only", "title": "Only", "cardIds": ["card-10"]}],
        "cards": {
            "card-10": {
                "id": "card-10",
                "title": "Survive restart",
                "details": "This should still be present after restart.",
            }
        },
    }

    with TestClient(app) as first_client:
        put_response = first_client.put("/api/board", json=next_board)
        assert put_response.status_code == 200

    with TestClient(app) as second_client:
        get_response = second_client.get("/api/board")
        assert get_response.status_code == 200
        assert get_response.json()["cards"]["card-10"]["title"] == "Survive restart"
