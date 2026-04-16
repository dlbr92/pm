import json
import sqlite3

from app.db import get_board_json, get_or_create_user, init_db, save_board_json


def test_init_db_creates_file_and_tables(tmp_path) -> None:
    db_path = tmp_path / "data" / "app.db"
    init_db(db_path)

    assert db_path.exists()

    with sqlite3.connect(db_path) as connection:
        tables = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()

    table_names = {table[0] for table in tables}
    assert "users" in table_names
    assert "boards" in table_names


def test_board_json_round_trip_by_user_id(tmp_path) -> None:
    db_path = tmp_path / "data" / "app.db"
    init_db(db_path)

    user_id = get_or_create_user("user", db_path)
    assert get_board_json(user_id, db_path) is None

    board_v1 = json.dumps(
        {"columns": [{"id": "todo", "title": "To Do"}], "cards": []},
        sort_keys=True,
    )
    save_board_json(user_id, board_v1, db_path)
    assert json.loads(get_board_json(user_id, db_path) or "{}") == json.loads(board_v1)

    board_v2 = json.dumps(
        {
            "columns": [{"id": "todo", "title": "Backlog"}],
            "cards": [{"id": "card-1", "title": "Test card", "columnId": "todo"}],
        },
        sort_keys=True,
    )
    save_board_json(user_id, board_v2, db_path)
    assert json.loads(get_board_json(user_id, db_path) or "{}") == json.loads(board_v2)
