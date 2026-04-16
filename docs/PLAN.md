# Project plan checklist

This document defines the execution plan for the MVP Project Management web app.
Each part includes implementation steps, tests, and explicit success criteria.

## Confirmed decisions

- Single Docker container for the full app (FastAPI + built static frontend).
- Use `OPENAI_API_KEY` (no OpenRouter).
- Keep auth lightweight and frontend-driven for MVP (`user` / `password`).
- Use a sensible local SQLite path (default: `backend/data/app.db`).
- Store Kanban as JSON in SQLite (single board JSON payload per user).
- Choose the simplest modern testing approach.

## Standard test approach (simple + current)

- Backend: `pytest` + `httpx`/FastAPI test client.
- Frontend unit/component: `vitest` + `@testing-library/react`.
- Integration/e2e: `playwright` with focused smoke flows.

## Part 1: Plan and alignment

### Checklist

- [x] Expand `docs/PLAN.md` into actionable phase checklists (this document).
- [x] Create `frontend/AGENTS.md` describing the existing frontend structure and key behaviors.
- [x] Confirm plan approval with user before starting implementation.

### Tests

- [x] N/A (planning/documentation phase).

### Success criteria

- [x] Plan is explicit enough to execute phase-by-phase with minimal ambiguity.
- [x] User has approved plan content before coding starts.

## Part 2: Scaffolding

### Checklist

- [x] Create `backend/` FastAPI app skeleton.
- [x] Add Dockerfile and supporting config for single-container build/run.
- [x] Add `scripts/` start/stop scripts for Windows, macOS, Linux.
- [x] Add basic health endpoint (example: `/api/health`).
- [x] Serve example static HTML from `/` to verify container plumbing.

### Tests

- [x] Backend unit test for health endpoint.
- [x] Local run test: container starts and serves `/` + `/api/health`.
- [x] Script smoke tests: each start/stop script executes expected commands.

### Success criteria

- [x] `docker run` starts app successfully.
- [x] `GET /` returns example HTML.
- [x] `GET /api/health` returns success JSON.

## Part 3: Frontend static integration

### Checklist

- [x] Build existing `frontend/` app for production output.
- [x] Configure FastAPI static serving so Kanban demo is served at `/`.
- [x] Ensure frontend assets resolve correctly in container.

### Tests

- [x] Frontend unit tests for core board rendering.
- [x] Integration smoke test: board loads at `/` when app runs through backend.

### Success criteria

- [x] Demo Kanban UI renders from backend-served static bundle.
- [x] No broken static assets in container runtime.

## Part 4: Fake sign-in flow (MVP)

### Checklist

- [x] Add login screen on first visit.
- [x] Validate fixed credentials (`user` / `password`) in frontend logic.
- [x] Store lightweight logged-in state in frontend (session/local storage).
- [x] Add logout path and redirect back to login.

### Tests

- [x] Unit tests for login form behavior and validation.
- [x] Integration tests for login success/failure and logout flow.
- [x] E2E smoke: cannot access board without login state.

### Success criteria

- [x] Unauthenticated users see login view.
- [x] Valid credentials grant access to Kanban.
- [x] Logout reliably returns to login state.

## Part 5: Database modeling

### Checklist

- [x] Define SQLite schema for users + board JSON storage.
- [x] Proposed minimal tables:
  - `users(id, username, created_at)`
  - `boards(id, user_id, board_json, updated_at)`
- [x] Add migration/init logic to create DB if missing.
- [x] Document schema and rationale in `docs/`.
- [x] Request user sign-off on schema documentation.

### Tests

- [x] Unit tests for DB init/create-if-missing behavior.
- [x] CRUD tests for board JSON read/write by `user_id`.

### Success criteria

- [x] Fresh startup creates DB and required tables.
- [x] Board JSON round-trips without data loss.
- [x] Schema documentation approved by user.

## Part 6: Backend Kanban API

### Checklist

- [x] Implement API routes to fetch/update board for authenticated MVP user.
- [x] Add request/response models with validation.
- [x] Add service/repository layer for DB interactions (simple and clear).
- [x] Ensure all updates persist to SQLite JSON field.

### Tests

- [x] Endpoint tests for successful board fetch/update.
- [x] Negative tests for invalid payloads.
- [x] Persistence tests confirming data survives app restart.

### Success criteria

- [x] Backend API can fully read and update board state.
- [x] Validation errors are clear and consistent.
- [x] Data persists in SQLite as expected.

## Part 7: Frontend + backend wiring

### Checklist

- [ ] Replace frontend local-only board state with backend API calls.
- [ ] Load board on app start after login.
- [ ] Persist card edits/moves/column changes through API.
- [ ] Handle loading/error states in a minimal user-friendly way.

### Tests

- [ ] Frontend tests for API integration paths.
- [ ] Integration tests for create/edit/move persistence.
- [ ] E2E flow: refresh page and verify board state is retained.

### Success criteria

- [ ] Board interactions persist across refresh/restart.
- [ ] Frontend and backend stay in sync for core board actions.

## Part 8: AI connectivity

### Checklist

- [ ] Add backend AI client using `OPENAI_API_KEY`.
- [ ] Use model `openai/gpt-oss-120b` per project requirements.
- [ ] Add diagnostic endpoint/task to test AI call with prompt `2+2`.
- [ ] Add basic timeout/error handling for failed upstream calls.

### Tests

- [ ] Unit tests with mocked AI client responses.
- [ ] Optional live connectivity test (enabled only when key exists).

### Success criteria

- [ ] Backend can successfully call model and return expected reply for `2+2`.
- [ ] Failures are handled gracefully with clear errors.

## Part 9: AI structured board updates

### Checklist

- [ ] Define strict structured output schema for chat response + optional board update.
- [ ] Send current board JSON + user message + conversation history to model.
- [ ] Parse/validate model output before applying board changes.
- [ ] Apply optional board update atomically when present.

### Tests

- [ ] Unit tests for schema validation and parser behavior.
- [ ] Tests for both response-only and response+board-update cases.
- [ ] Failure tests for malformed model outputs.

### Success criteria

- [ ] AI responses are reliably parsed into typed structure.
- [ ] Valid board updates persist correctly; invalid updates are rejected safely.

## Part 10: AI sidebar UX

### Checklist

- [ ] Add sidebar chat UI integrated with backend AI endpoint.
- [ ] Display conversation history and loading/error states.
- [ ] Apply returned board updates and refresh UI state automatically.
- [ ] Keep styling aligned with project color scheme.

### Tests

- [ ] Component tests for chat interactions and state rendering.
- [ ] Integration tests for AI response rendering + board update application.
- [ ] E2E flow where AI modifies board and UI reflects changes immediately.

### Success criteria

- [ ] User can chat in sidebar without breaking Kanban interactions.
- [ ] AI-triggered board updates appear in UI automatically.
- [ ] Core UX remains stable and responsive.

## Execution order and gates

- [ ] Complete parts strictly in order.
- [ ] Pause for user approval after major planning/schema milestones (Part 1, Part 5).
- [ ] Keep scope to MVP only; no extra features beyond requirements.