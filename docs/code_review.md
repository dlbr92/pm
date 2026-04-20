# Code review

Reviewed against the full codebase as of the current commit. Findings are calibrated to the MVP scope — issues that are by-design for a local single-user Docker app are noted as such and not elevated to bugs.

---

## Bugs

### [HIGH] Race condition: concurrent board saves can overwrite state

**File:** `frontend/src/app/page.tsx:73–87`

`handleBoardChange` applies an optimistic update then fires `saveBoard()` (a floating promise). If the user triggers two changes in quick succession — a card drag followed immediately by a column rename — two `saveBoard` calls are in flight simultaneously. Whichever resolves last calls `setBoard(persistedBoard)`, overwriting the more recent local state. The board visually reverts.

**Fix:** Cancel the previous in-flight save before starting a new one (e.g., an `AbortController` ref), or skip the `setBoard(persistedBoard)` echo since the server just mirrors what was sent.

---

### [MEDIUM] AI response always overwrites board, including during in-flight saves

**File:** `frontend/src/app/page.tsx:100`

`handleSendAIMessage` ends with `setBoard(response.board)`. The backend fetches the board from the database at the start of `AIChatService.run()`. If the user made a board change whose `PUT /api/board` hasn't finished yet when they also send an AI message, the AI response will contain the pre-change board, and `setBoard` will revert the optimistic update.

**Fix:** Only call `setBoard` when `response.boardUpdated` is `true`. When the AI makes no board change, leave the local state alone.

```typescript
if (response.boardUpdated) {
  setBoard(response.board);
}
```

---

### [LOW] Column can reference a card ID that appears in another column

**File:** `backend/app/schemas/board.py:38–47`

`BoardModel`'s `column_card_references_must_exist` validator checks that each `cardId` in a column exists in `cards`, but does not check for duplicates across columns. A card ID could appear in two columns simultaneously. The AI could produce such a board; it would pass validation and be persisted.

**Fix:** Add a cross-column uniqueness check to the model validator.

```python
seen = set()
for column in self.columns:
    for card_id in column.cardIds:
        if card_id in seen:
            raise ValueError(f"Card '{card_id}' appears in more than one column.")
        seen.add(card_id)
```

---

## Error handling

### [MEDIUM] `response.json()` is not guarded against parse failure

**Files:** `frontend/src/lib/boardApi.ts:9`, `frontend/src/lib/aiChatApi.ts:32`

Both API clients call `response.json()` without a try/catch. If the server returns a non-JSON body (e.g., an nginx error page or a proxy 502), the `.json()` call throws a `SyntaxError` that propagates with no context and no user-facing message. The existing `response.ok` guard does not protect against this.

**Fix:** Wrap `.json()` in a try/catch that throws a clear `Error("Unexpected response from server.")`.

---

### [LOW] Start scripts do not validate `.env` exists before `docker run`

**Files:** `scripts/start.ps1:19`, `scripts/start-mac.sh`, `scripts/start-linux.sh`

All three scripts pass `--env-file .env` to `docker run`. If `.env` is absent, Docker exits with a terse error that doesn't explain the cause.

**Fix:** Add a guard before the `docker run` call:

```powershell
if (-not (Test-Path .env)) {
  Write-Error ".env file not found. Copy .env.example and fill in your keys."
  exit 1
}
```

---

## Code quality

### [MEDIUM] DEFAULT_BOARD is duplicated between frontend and backend

**Files:** `backend/app/services/board_service.py:7–61`, `frontend/src/lib/kanban.ts` (`initialData`)

Both sides define the same 5-column, 8-card seed board independently. The backend `DEFAULT_BOARD` is the authoritative source (it's what gets persisted to SQLite on first load), but the frontend `initialData` is still used in tests and Playwright mocks. If the board structure diverges, tests will pass against a stale shape.

**Fix:** Keep `initialData` in `kanban.ts` as a test/dev fixture but add a comment noting it must be kept in sync with `board_service.DEFAULT_BOARD`. Alternatively, expose `/api/board/default` and use it in Playwright setup instead.

---

### [LOW] No `maxLength` on card title, details, or column title inputs

**Files:** `frontend/src/components/NewCardForm.tsx:37–43`, `frontend/src/components/KanbanColumn.tsx:44`

Inputs are unbounded. Pasting a very long string doesn't break persistence (the backend stores arbitrary JSON), but it breaks the Kanban card layout and column header at practical screen widths.

**Fix:** Add `maxLength` attributes on the inputs (`title` ~100 chars, `details` ~500 chars). Optionally mirror with `max_length` on the Pydantic fields for belt-and-suspenders.

---

## Type safety

### [LOW] API responses are cast with `as` rather than validated at runtime

**Files:** `frontend/src/lib/boardApi.ts:9`, `frontend/src/lib/aiChatApi.ts:32`

```typescript
return (await response.json()) as BoardData;
```

TypeScript erases this cast at runtime. If the backend ever returns a structurally different payload (schema change, partial update bug), the app receives it silently and crashes later at the point of access with no actionable error.

**Fix:** For an MVP this is acceptable. When the project grows, add a lightweight schema validator (e.g., Zod) at the API boundary to catch shape mismatches early.

---

## Test coverage gaps

### [MEDIUM] No frontend test for fetch/network failure paths

**File:** `frontend/src/app/page.test.tsx`

Tests mock successful API calls. There are no tests for:
- `fetchBoard` throwing (network down, server error) → should show load error + retry button
- `saveBoard` failing → should show save error
- `sendAIChat` failing → should show chat error

These paths exist and have UI, but are untested.

---

### [LOW] No backend test for the duplicate-card-across-columns validation gap

Now that the cross-column uniqueness check is absent (see bug above), there is also no test asserting the `PUT /api/board` endpoint rejects a board where the same card ID appears in two columns.

---

## Deployment / configuration

### [LOW] Database file has no explicit permissions set after creation

**File:** `backend/app/db.py:43–50`

`init_db()` creates the `data/` directory and SQLite file but does not set file permissions. On Linux inside the container, the file inherits the process umask. If the container is ever run in a shared environment, the database could be world-readable.

**Fix:** After creating the file, add:
```python
target_path.chmod(0o600)
```

---

## Out of scope for MVP (noted for awareness)

The following are intentional MVP trade-offs, not actionable items:

- **Hardcoded credentials** (`user` / `password`) — by design, documented in `AGENTS.md`
- **No CORS configuration** — frontend and backend share the same origin; not needed
- **No session token for API calls** — single-user MVP; the API is unauthed by design
- **No database migration tooling** — schema is stable; migrations can be added when schema changes are needed
- **`gpt-4.1-mini` model string hardcoded** — acceptable for a single-model MVP

---

## Summary

| Severity | Count | Items |
|----------|-------|-------|
| High | 1 | Concurrent save race condition |
| Medium | 3 | AI overwrites in-flight board, `response.json()` unguarded, no frontend error-path tests |
| Low | 6 | Duplicate card validation gap, duplicate DEFAULT_BOARD, no input `maxLength`, `as` casts, missing .env check, db file permissions |

The codebase is clean and well-structured for an MVP. The two race conditions (HIGH + MEDIUM) are the only issues likely to surface in normal use.
