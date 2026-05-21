# AGENTS.md

Short operating card for AI coding agents. Full contract: `CLAUDE.md`.

## What this app is
LingosAI — a strict AI English coach. Loop: **diagnose → profile → fixed
curriculum → personalized daily activities → AI evaluation → corrective
feedback → deterministic scoring → progress/streak**. Never generic chat,
never generic praise.

## Stack
- Backend: FastAPI · SQLAlchemy 2 · Alembic · Pydantic v2 · Postgres · `uv`
- AI: OpenAI · LangChain · LangGraph · LangSmith · Azure Speech
- Frontend: Next.js 16 (App Router) · React 19 · TanStack Query · Zustand · Tailwind v4
- Tests: pytest (+asyncio), ruff, mypy; node --test on frontend

## Setup
```bash
# backend
cd backend && uv sync && uv run alembic upgrade head
cd backend && uv run uvicorn app.main:app --reload
# or from repo root: ./scripts/dev-backend.sh

# frontend
cd frontend && npm install && npm run dev

# dev deps
docker compose up -d
```

## Test / lint / build
```bash
# backend
uv run pytest
uv run ruff check app tests
uv run ruff format app tests
uv run mypy app

# frontend
npm run lint
npm run build
npm run test:admin
npx tsc --noEmit
```

## Code style
- Backend: `routes → service → repository → models`, Pydantic schemas per module.
- Frontend: API in `src/lib/*-api.ts`, hooks in `src/hooks/`, stores in
  `src/store/`. **No business logic in components.**
- Type everything. Prefer small diffs. Follow existing patterns.

## Architecture rules
- Curriculum structure is **fixed**. AI personalizes only inside template slots.
- **Scoring math is pure** (`app/scoring/`). No I/O, no randomness.
  LLMs return `raw_score` + mistakes; tiers/rewards are code.
- All LLM calls live under `app/ai/`. Routes/services don't call OpenAI directly.
- Evaluation must produce structured mistakes. Feedback consumes them and
  must be specific + corrective.
- No WebSocket layer wired today — session flow is REST.

## Safety rules
- Never edit existing Alembic migrations — add a new revision.
- Never change DB schema without a migration + rollback note.
- Never break existing API response shapes.
- Never change scoring formulas without auditing `progress/`, `streaks/`,
  dashboard, and `scoring_writer.py`.
- Never hardcode secrets or invent env vars without updating
  `.env.example` and `core/config.py`.
- Never fake or skip tests. Never disable hooks/CI.
- Verify before changing: `learning_session/` (legacy?), `ai/graphs/`
  (empty), `curriculum/` v1↔v2 split, Pinecone/Celery/Redis wiring.

## Definition of done
- Matches the request; preserves existing behavior / API shapes.
- Tests + lint pass on touched paths (or failure is reported clearly).
- New behavior has at least one test, or the gap is called out.
- Final reply: files changed, checks run, risks, next step, docs updated.
