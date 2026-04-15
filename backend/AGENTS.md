# Backend snapshot

This backend is a minimal FastAPI scaffold extended through Part 3.

## Current behavior

- `GET /` serves static web content:
  - `backend/frontend-static/` when a built frontend export is present.
  - `backend/static/` as local fallback (hello page) when no export is present.
- `GET /api/health` returns:
  - `{"status":"ok","service":"backend"}`
- Static web content is mounted at `/` (HTML mode).

## Structure

- `app/main.py`: FastAPI app setup, routes, static mount.
- `static/index.html`: "hello world" page with a button that calls `/api/health`.
- `frontend-static/`: generated Next.js static export copied during Docker build.
- `tests/test_health.py`: unit tests for root + health endpoint.
- `requirements.txt`: runtime dependencies.
- `requirements-dev.txt`: test dependencies.

## Run targets

- Local dev server command:
  - `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- Container command:
  - same as above via `Dockerfile`.