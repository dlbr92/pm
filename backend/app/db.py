import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "app.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    board_json TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def get_db_path(db_path: Path | None = None) -> Path:
    if db_path is not None:
        return db_path

    env_path = os.getenv("PM_DB_PATH")
    if env_path:
        return Path(env_path)

    return DEFAULT_DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    target_path = get_db_path(db_path)
    connection = sqlite3.connect(target_path)
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db(db_path: Path | None = None) -> Path:
    target_path = get_db_path(db_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with get_connection(target_path) as connection:
        connection.executescript(SCHEMA_SQL)

    return target_path


def get_or_create_user(username: str, db_path: Path | None = None) -> int:
    with get_connection(db_path) as connection:
        connection.execute(
            "INSERT OR IGNORE INTO users(username) VALUES (?);",
            (username,),
        )
        row = connection.execute(
            "SELECT id FROM users WHERE username = ?;",
            (username,),
        ).fetchone()

    if row is None:
        raise ValueError(f"User lookup failed for username: {username}")

    return int(row[0])


def get_board_json(user_id: int, db_path: Path | None = None) -> str | None:
    with get_connection(db_path) as connection:
        row = connection.execute(
            "SELECT board_json FROM boards WHERE user_id = ?;",
            (user_id,),
        ).fetchone()

    if row is None:
        return None

    return str(row[0])


def save_board_json(user_id: int, board_json: str, db_path: Path | None = None) -> None:
    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO boards(user_id, board_json)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                board_json = excluded.board_json,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (user_id, board_json),
        )
