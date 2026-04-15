# Frontend snapshot: Kanban demo + MVP auth

This document describes the current frontend implementation in `frontend/`.
It is a baseline reference for upcoming backend and AI integration work.

## Current scope

- Next.js app-router project with a single route (`/`) with login gate + Kanban board.
- Frontend-only auth using fixed credentials: `user` / `password`.
- Session state stored in `sessionStorage` key `pm-authenticated`.
- Client-side only board state (no API calls, no persistence yet).
- Drag-and-drop cards across columns, rename columns, add cards, delete cards.
- Styling follows the project color palette defined in CSS variables.

## Tech stack

- Next.js 16 + React 19 + TypeScript
- Tailwind CSS v4
- `@dnd-kit` for drag-and-drop (`core`, `sortable`, `utilities`)
- `clsx` for conditional classes
- Vitest + Testing Library for unit/component tests
- Playwright for e2e smoke tests

## App structure

- `src/app/page.tsx`
  - Home route; enforces login state and renders either `LoginForm` or `KanbanBoard`.
- `src/components/LoginForm.tsx`
  - Login UI and invalid-credential error handling.
- `src/components/KanbanBoard.tsx`
  - Main state container for board + drag interaction wiring; includes logout button when provided.
- `src/components/KanbanColumn.tsx`
  - Column UI, inline title editing, droppable area, card list, add-card form.
- `src/components/KanbanCard.tsx`
  - Sortable card UI with remove action.
- `src/components/NewCardForm.tsx`
  - Expand/collapse form for creating cards in a column.
- `src/components/KanbanCardPreview.tsx`
  - Drag overlay card preview.
- `src/lib/kanban.ts`
  - Domain types (`Card`, `Column`, `BoardData`), seed data, `moveCard`, `createId`.
- `src/lib/auth.ts`
  - Auth constants and credential validator.

## Data model and behavior

- Board model:
  - `columns: Column[]` where each column has ordered `cardIds`.
  - `cards: Record<string, Card>` keyed by card id.
- Initial board includes five fixed columns:
  - Backlog, Discovery, In Progress, Review, Done.
- Column rename updates `column.title` inline.
- Add card:
  - Creates ID via `createId("card")`.
  - Adds new card object to `cards`.
  - Appends ID to target column `cardIds`.
- Delete card:
  - Removes card entry from `cards`.
  - Removes card ID from the owning column.
- Drag/drop:
  - Reorder within same column.
  - Move between columns.
  - Drop on column container appends to end.

## Styling and design tokens

- Global CSS lives in `src/app/globals.css`.
- Color tokens align with project palette:
  - `--accent-yellow`, `--primary-blue`, `--secondary-purple`, `--navy-dark`, `--gray-text`.
- Layout emphasizes a single-board workspace with five-column grid on large screens.

## Testing status

- Unit/component tests:
  - `src/app/page.test.tsx` covers login gate, valid/invalid auth, and logout.
  - `src/components/LoginForm.test.tsx` covers form validation behavior.
  - `src/components/KanbanBoard.test.tsx` covers render, rename, add/remove card.
  - `src/lib/kanban.test.ts` covers `moveCard` reorder and cross-column moves.
- E2E tests:
  - `tests/kanban.spec.ts` validates login requirement, board load, add card, and drag card between columns.
- Commands:
  - `npm run test:unit`
  - `npm run test:e2e`
  - `npm run test:all`

## Constraints for future changes

- Keep the existing Kanban interactions stable while introducing backend persistence.
- Preserve current visual direction and palette unless explicitly updated by plan.
- Favor small, incremental changes with tests at each phase.
