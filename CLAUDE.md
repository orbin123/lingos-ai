# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

LingosAI is an AI English-tutoring platform. A learner follows a multi-week curriculum of daily lessons; each lesson is a chat-driven session of teaching → task → evaluation → feedback. The backend uses LLMs (via LangChain/LangGraph) to generate tasks, evaluate answers, and produce personalized feedback, with RAG-backed "feedback memory" so the tutor remembers a learner's recurring weaknesses.

- **Backend**: FastAPI + SQLAlchemy 2.0 + PostgreSQL, package-managed by `uv` (Python ≥3.11). AI via LangChain/LangGraph + OpenAI; Pinecone for vectors; Azure Speech for pronunciation.
- **Frontend**: Next.js 16 (App Router) + React 19 + TypeScript, TanStack Query for server state, Zustand for client state, Tailwind v4.
- **Infra**: Docker Compose runs Postgres + Redis only (the apps run on the host, not in containers).

## Commands

### Backend (run from `backend/`)
```bash
uv sync                                   # install deps
uv run alembic upgrade head               # apply migrations
uv run uvicorn app.main:app --reload      # API at http://127.0.0.1:8000 (docs at /docs)
uv run pytest                             # all tests
uv run pytest tests/test_session_lifecycle.py            # single file
uv run pytest tests/test_session_lifecycle.py::test_name # single test
uv run ruff check .                       # lint
uv run mypy app                           # type-check
uv run alembic revision --autogenerate -m "msg"  # new migration
```
From the repo root, `./scripts/dev-backend.sh` is a shortcut for the uvicorn command (`chmod +x` once).

### Frontend (run from `frontend/`)
```bash
npm run dev            # dev server at http://localhost:3000
npm run build
npm run lint
npm run test:admin     # node --test tests/*.test.mjs  (the only JS test suite)
```

### Infra
```bash
docker compose up -d   # Postgres + Redis (ports come from .env)
```

## Environment & config

- All backend config flows through `app/core/config.py` (`pydantic-settings`). It reads the **single repo-root `.env`** (`env_file="../.env"`, relative to `backend/`). Missing required vars crash the app at startup — that's intentional. Copy `.env.example` to `.env` to start.
- `settings.database_url` is given as `postgresql://…`; `app/core/database.py` rewrites it to `postgresql+psycopg://…` (psycopg 3). Don't hardcode the driver in the URL.
- Tests don't need a real `.env`: `tests/conftest.py` sets dummy env vars and a SQLite `DATABASE_URL` before settings load.
- The standalone `backend/check_*.py` and `delete_bugged_session.py` scripts are ad-hoc DB debugging tools with hardcoded local connection strings — not part of the app.

## Backend architecture

### Module layering
Each feature lives in `app/modules/<name>/` and follows a strict layered pattern. Respect it when adding code:

```
routes.py / router.py  → HTTP/WS endpoints (thin; depend on get_db, get_current_user)
service.py             → business logic, owns transaction commits at logical boundaries
repository.py          → all DB queries (the only layer that touches the ORM session directly)
models.py              → SQLAlchemy ORM models for this module
schemas.py             → Pydantic request/response models
exceptions.py          → domain exceptions (routes translate these to HTTPException)
```

Routes are registered in `app/main.py` via `include_router`. Services receive collaborators (evaluators, feedback generators, repositories) by injection so the LLM-backed implementations can be swapped for stubs in tests.

### Model registry — important
`app/models.py` imports **every** ORM model from every module. This populates SQLAlchemy's registry so cross-module `relationship()` string references resolve and Alembic can discover all tables via `Base.metadata`. **When you add a new model, add it to `app/models.py`** or migrations and relationships will silently break. `Base` is defined in `app/core/database.py`.

### The session domain (the core of the app)
There are two related but distinct session concepts — don't conflate them:

- **`app/modules/sessions/`** — the V2 "daily session" engine. `SessionService` owns the start → next-activity → submit → complete → scorecard lifecycle and **all** evaluation/feedback DB writes. It composes injected `Evaluator` and `FeedbackGenerator` (LLM-backed in prod, stubs in tests).
- **`app/modules/learning_session/`** — the chat/WebSocket layer that drives a session turn-by-turn for the UI. Its `orchestrator.py` is deliberately "dumb": it does **not** decide lesson flow. The curriculum blueprint + V2 session rows already determine which activities exist and in what order; the orchestrator only turns that deterministic data into structured WebSocket events (`learning_session.event.v1`).

### Curriculum: file-authored vs DB-seeded
Curriculum can come from **authored Python dataclasses** (`app/modules/curriculum/data/source_24w.py`, keyed by `(week_number, day_index 0..6)`) or from **DB-seeded** `CurriculumDay` rows. `app/modules/curriculum/file_source.py` is the bridge: when a day is file-authored, its archetype order, task specs, teacher instructions, and eval/feedback overrides **take precedence** over the DB. Authored teacher behaviour is smuggled through the existing `teacher_instructions` column under the `SCRIPTED_PLAN_KEY` (`__scripted_plan`) sentinel.

### AI layer (`app/ai/`)
- Each AI capability is a subpackage with the same shape: `interface.py` (abstract contract) + a concrete client (`openai_client.py`, `azure_client.py`) + `exceptions.py`, plus a `get_default_*_service()` factory. Capabilities: `llm`, `tts`, `stt`, `pronunciation` (Azure), `imagegen`, `embeddings`.
- `app/ai/agents/` holds the prompt-driven agents (teacher, evaluator, feedback, planner, task_generator, personalization, ielts). Prompts are Markdown files loaded by `prompt_loader.py` via slash-delimited names (e.g. `ielts/generator`) with `{{variable}}` placeholders rendered by `render_prompt_template` (does not interpret JSON braces).
- `app/ai/graphs/` is the LangGraph definition. The compiled graph documents the flow and is used in tests; the live chat flow is driven from the WebSocket layer, and DB writes are owned by `SessionService.submit_activity`, not by graph nodes.
- LangSmith tracing is on by default (`LANGCHAIN_TRACING_V2=True`).

### Generated media
TTS audio and generated images are written to disk by `LocalBlobStorage` under `app/ai/{tts,stt,imagegen,pronunciation}/_cache` and served directly via FastAPI `StaticFiles` mounts (`/audio`, `/images`). Cache dirs are configurable in `config.py`. In prod these would move to object storage + CDN.

### Auth & admin
- JWT bearer auth. `app/modules/auth/dependencies.py` provides `get_current_user` (decodes JWT `sub`, loads the user). Google OAuth is supported; `redirect_slashes=False` in `main.py` is deliberate to avoid a 307 on the OAuth callback.
- Role-based access: `learner`, `admin`, `super_admin` backed by `Role`/`Permission`/`RolePermission`/`UserRole`. Super-admins manage roles and subscriptions; normal admins get scoped reads (e.g. `payments.read`).
- `AdminRateLimitMiddleware` (`app/core/rate_limit.py`) rate-limits admin/login routes.
- Admin mutations are recorded to audit logs (`app/modules/admin/audit_service.py`). Billing tables store **only provider IDs** (masked in admin views) — never raw payment data.

## Frontend architecture

- **App Router** under `src/app/`. Route groups like `(auth)` and dynamic segments like `sessions/[sessionId]` are in use. Admin pages live under `src/app/admin/`.
- **API access**: one shared axios instance in `src/lib/api.ts`. It auto-attaches the JWT from `localStorage` and, on a `401` from a non-auth endpoint, clears the token and redirects to `/login`. Per-domain wrappers (`sessions-api.ts`, `auth-api.ts`, `challenges-api.ts`, etc.) build on it — add new calls to the matching `*-api.ts`, don't create new axios instances. Base URL comes from `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).
- **Server state** via TanStack Query (`src/providers/query-provider.tsx`); domain hooks in `src/hooks/` (e.g. `useSessionsFlow`, `useNextTask`). **Client state** via Zustand stores in `src/store/` (`authStore`, `sessionStore`, `taskStore`, `diagnosisStore`).
- **Chat UI** is component-driven: `src/components/chat/` with `tasks/`, `feedback/`, `teaching/`, `evaluation/` subfolders and per-widget renderers. Backend widget keys are normalized to stable snake_case by `app/modules/sessions/widget_mapping.py` — keep that mapping in sync when adding task/widget types on either side.
- `@/*` path alias maps to `src/*` (tsconfig). TypeScript `strict` is on.

## Conventions

- Backend: keep DB access in repositories, business logic + commits in services, and routes thin. Raise domain exceptions; translate to HTTP at the route boundary.
- New ORM model → register it in `app/models.py` and generate an Alembic migration.
- New task/widget type → update both the backend widget mapping and the corresponding `src/components/chat/` renderer.


