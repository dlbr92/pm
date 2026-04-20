# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Full-stack Project Management / Kanban board web app with AI chat capabilities. The frontend is a Next.js static export served by a Python FastAPI backend, all packaged in a single Docker container. SQLite stores board state per user; OpenAI (`gpt-4.1-mini`) drives AI-assisted board updates.

## Commands

### Frontend (`frontend/`)
```bash
npm run dev           # Dev server
npm run build         # Static export (output in out/)
npm run lint          # ESLint
npm run test:unit     # Vitest unit tests
npm run test:unit:watch
npm run test:e2e      # Playwright e2e tests
npm run test:all      # Unit + e2e
```

### Backend (`backend/`)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000   # Dev server
pytest                                              # All tests
pytest -v                                          # Verbose
```

### Docker (from repo root)
```bash
docker build -t pm-mvp .
docker run -d --name pm-mvp -p 8000:8000 --env-file .env pm-mvp

# Convenience scripts (Mac/Linux/Windows):
./scripts/start-mac.sh        # or start-linux.sh / start.ps1
./scripts/stop-mac.sh         # --no-build flag skips image rebuild
```

## Architecture

### Frontend (`frontend/src/`)
- **`app/page.tsx`** — Root route: orchestrates auth check, board fetch, and renders `KanbanBoard` + `AIChatSidebar`
- **`components/`** — `KanbanBoard` (state container) → `KanbanColumn` → `KanbanCard`; drag-and-drop via `@dnd-kit`; `AIChatSidebar` for chat UI; `LoginForm` for session auth
- **`lib/boardApi.ts`** — REST client for `GET/PUT /api/board`
- **`lib/aiChatApi.ts`** — REST client for `POST /api/ai/chat`
- **`lib/kanban.ts`** — Domain models (`BoardModel`, `CardModel`, `ColumnModel`) and `moveCard` logic
- **`lib/auth.ts`** — Credential validation and `sessionStorage`-based session management

Auth is frontend-only: credentials are hardcoded (`user` / `password`), stored in `sessionStorage`. The DB is multi-user capable but the MVP always uses username `"user"`.

### Backend (`backend/app/`)
- **`main.py`** — FastAPI app with lifespan DB init; routes: `/api/health`, `/api/board` (GET/PUT), `/api/ai/chat`, `/api/ai/diagnostic`; mounts `frontend-static/` at `/`
- **`services/board_service.py`** — Thin wrapper around `BoardRepository`
- **`services/ai_service.py`** — OpenAI client wrapper with error handling
- **`services/ai_chat_service.py`** — Orchestrates: sends board + history + message to OpenAI, validates structured JSON response (`AIChatModelOutput`), applies board update if present
- **`repositories/board_repository.py`** — Loads/saves board JSON by username via `db.py`
- **`db.py`** — SQLite helpers; tables: `users`, `boards` (board stored as JSON blob per user)
- **`schemas/`** — Pydantic models for API contracts and AI output validation

### Data Flow

**Board changes** (drag, edit, add card): optimistic React state update → `PUT /api/board` saves full board JSON.

**AI chat**: `POST /api/ai/chat` with `{message, history}` → backend sends `{current_board, history, message}` to OpenAI → OpenAI returns `{reply, board_update: null | BoardModel}` → if board_update present, persist and return updated board to frontend.

### Environment
- `.env` at repo root must contain `OPENAI_API_KEY`
- `PM_DB_PATH` env var sets SQLite path (default: `backend/data/app.db`)
- Docker passes `.env` via `--env-file`

### Testing Conventions
- Backend tests mock `AIService` to avoid live API calls
- Frontend unit tests use Vitest + Testing Library (jsdom)
- Playwright e2e tests cover login, board load, and drag-card flows
- Test files: `frontend/src/**/*.test.tsx`, `frontend/tests/*.spec.ts`, `backend/tests/*.py`
