# Database schema (Part 5)

This MVP uses a local SQLite database at `backend/data/app.db` by default.

The path can be overridden with `PM_DB_PATH`.

## Tables

### `users`

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `username TEXT NOT NULL UNIQUE`
- `created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP`

Purpose:
- Stores one row per user.
- Supports future multi-user expansion while keeping MVP auth simple.

### `boards`

- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `user_id INTEGER NOT NULL UNIQUE`
- `board_json TEXT NOT NULL`
- `updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP`
- `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

Purpose:
- Stores one board JSON payload per user.
- Keeps schema minimal for MVP while preserving full board state in one value.

## Why JSON storage for board state

- The MVP needs fast iteration and simple persistence.
- The frontend board shape already exists as JSON.
- A single JSON payload avoids premature normalization for cards/columns.
- This can evolve later to normalized tables without blocking MVP delivery.

## Init and migration strategy (MVP)

- On backend startup, the app runs DB initialization.
- If DB file/folder does not exist, it is created.
- `CREATE TABLE IF NOT EXISTS` is used for idempotent startup.
- No external migration tool is introduced yet to keep the MVP simple.
