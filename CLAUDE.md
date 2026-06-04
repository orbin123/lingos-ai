11# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

LingosAI is an AI English-tutoring platform. A learner follows a multi-week curriculum of daily lessons; each lesson is a chat-driven session of teaching → task → evaluation → feedback. The backend uses LLMs (via LangChain/LangGraph) to generate tasks, evaluate answers, and produce personalized feedback, with RAG-backed "feedback memory" so the tutor remembers a learner's recurring weaknesses. Scoring is a **separate deterministic (no-LLM) engine** that turns graded activities into per-sub-skill points and a dashboard score.

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
- The standalone `backend/check_*.py`, `delete_bugged_session.py`, and repo-root `test_db.py` scripts are ad-hoc DB debugging tools with hardcoded local connection strings — not part of the app. The root `backup*.sql` files are local DB dumps.

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

Not every module has all layers (e.g. `responses/` is route-only; `skills/` is models + repository). Routes are registered in `app/main.py` via `include_router`. Services receive collaborators (evaluators, feedback generators, repositories) by injection so the LLM-backed implementations can be swapped for stubs in tests.

The modules: `auth`, `admin`, `sessions`, `learning_session`, `curriculum`, `challenges`, `diagnosis`, `progress`, `streaks`, `preferences`, `subscriptions`, `responses`, `skills`, `personalization`, `feedback_memory`.

### Model registry — important
`app/models.py` imports **every** ORM model from every module. This populates SQLAlchemy's registry so cross-module `relationship()` string references resolve and Alembic can discover all tables via `Base.metadata`. **When you add a new model, add it to `app/models.py`** or migrations and relationships will silently break. `Base` is defined in `app/core/database.py`; shared column mixins (`IDMixin`, `CreatedAtMixin`, `TimestampMixin`) live in `app/core/mixins.py`.

### The session domain (the core of the app)
There are two related but distinct session concepts — don't conflate them:

- **`app/modules/sessions/`** — the V2 "daily session" engine. `SessionService` owns the start → next-activity → submit → complete → scorecard lifecycle and **all** evaluation/feedback DB writes. It composes injected `Evaluator` and `FeedbackGenerator` (LLM-backed in prod, stubs in tests). `planner.py` decides activity order; `scoring_writer.py` pushes the final scorecard into the learner's `SkillPoints` (replay-guarded: only the first attempt earns points).
- **`app/modules/learning_session/`** — the chat/WebSocket layer that drives a session turn-by-turn for the UI. Its `orchestrator.py` is deliberately "dumb": it does **not** decide lesson flow. The curriculum blueprint + V2 session rows already determine which activities exist and in what order; the orchestrator only turns that deterministic data into structured WebSocket events (`learning_session.event.v1`). It also exposes a REST router for hydrating chat state on reload.

### Archetype contracts — the runtime backbone
`app/modules/sessions/contracts/registry.py` is the **single source of truth** tying each activity *archetype* to its task widget, the agents that run it, the render widgets, and the strict Pydantic I/O schemas (`agent_inputs.py`, `task_payloads.py`, `evaluation.py`, `feedback.py`, `projection.py`). The curriculum blueprint only references an `archetype_id`; the registry resolves everything else. It composes `app.scoring.ARCHETYPE_REGISTRY` rather than duplicating it and **fails at import time** if any registered archetype lacks a contract.

- Add a new *day* → write blueprint data only (no code in the registry changes).
- Add a new *kind* of activity → add one archetype to the scoring registry and one contract row here; it's then reusable forever.

### Scoring engine (`app/scoring/`) — deterministic, no LLM
Pure functions implementing the scoring math: **no DB calls, no I/O, no randomness — same inputs → same outputs.** `archetypes.py` holds the `ARCHETYPE_REGISTRY` (each archetype's UI widget, supported themes, CEFR range, sub-skill `weight_map`, and rubric); `engine.py` buckets raw scores into tiers, computes per-activity rewards (24w/48w course variants), distributes them across sub-skills, aggregates a session, caps totals, and converts to a 0–10 dashboard score; `constants.py` holds the locked numerical constants. The rationale for the numbers lives in `backend/RESTRUCTURE_DECISIONS.md`. Sessions/progress modules consume this engine — don't reimplement the math elsewhere.

### Task schemas (`app/tasks/schemas/`)
Typed Pydantic task-payload schemas (`task_schemas.py`) and the LLM structured-output schemas (`llm_output_schemas.py`) used to constrain generation. These are the validated contracts for generated task content (fill-in-blanks, MCQ, dialogue, etc.).

### Curriculum: file-authored vs DB-seeded
Curriculum can come from **authored Python dataclasses** (`app/modules/curriculum/data/source_24w.py`, keyed by `(week_number, day_index 0..6)`) or from **DB-seeded** `CurriculumDay` rows. `app/modules/curriculum/file_source.py` is the bridge: when a day is file-authored, its archetype order, task specs, teacher instructions, and eval/feedback overrides **take precedence** over the DB. Authored teacher behaviour is smuggled through the existing `teacher_instructions` column under the `SCRIPTED_PLAN_KEY` (`__scripted_plan`) sentinel. `blueprint_adapter.py` / `adapters.py` translate authored data into the runtime blueprint.

### Streaks coupling
`app/modules/streaks/service.py` has two entry points: `record_in_same_tx` is called from `SessionService.submit_activity` **after** an activity is evaluated but **before** the outer commit (it flushes so the unique constraint catches double-fires, but does NOT commit — the caller owns the transaction); `get_streak_data` is a pure read that builds the 91-day activity grid for the dashboard. The MVP freeze rule is strict (every missed day resets) but configurable via constants, no migration needed.

### Progress & points
`app/modules/progress/` owns `SkillPoints` (per-sub-skill running totals), `SkillPointsLog`, and `ProgressLog`. The diagnosis flow seeds points only (see `test_diagnosis_seeds_points_only`). The `skills/` module holds the canonical `Skill` rows.

### AI layer (`app/ai/`)
- Each AI *capability* is a subpackage with the same shape: `interface.py` (abstract contract) + a concrete client (`openai_client.py`, `azure_client.py`) + `exceptions.py`, plus a `get_default_*_service()` factory. Capabilities: `llm`, `tts`, `stt`, `pronunciation` (Azure), `imagegen`, `embeddings`.
- `app/ai/agents/` holds the prompt-driven agents (`teacher`, `evaluator`, `feedback`, `planner`, `task_generator`, `personalization`, and the `ielts_challenge/` agents — generator, evaluator, feedback, speaking evaluator). Prompts are Markdown files loaded by `prompt_loader.py` via slash-delimited names (e.g. `ielts/generator`) with `{{variable}}` placeholders rendered by `render_prompt_template` (does not interpret JSON braces).
- `app/ai/sessions/` holds the **LLM-backed session collaborators** the `SessionService` injects in prod: `llm_evaluator.py`, `llm_feedback.py`, `llm_task_generator.py`, `speaking_eval.py`, wired by `factory.py` (`build_default_agents`, `build_rag_services`). Tests swap these for stubs.
- `app/ai/graphs/` is the LangGraph definition. The compiled graph documents the flow and is used in tests; the live chat flow is driven from the WebSocket layer, and DB writes are owned by `SessionService.submit_activity`, not by graph nodes.
- LangSmith tracing is on by default (`LANGCHAIN_TRACING_V2=True`).

### Generated media
TTS audio and generated images are written to disk by `LocalBlobStorage` (`app/ai/storage/`) under `app/ai/{tts,stt,imagegen,pronunciation}/_cache` and served directly via FastAPI `StaticFiles` mounts (`/audio`, `/images`). Cache dirs are configurable in `config.py`. `POST /responses/transcribe-audio` (the `responses/` module) is what the speaking widgets post recordings to — it returns a transcript + audio URL that the evaluator/feedback grade on submit. In prod these would move to object storage + CDN.

### Auth & admin
- JWT bearer auth. `app/modules/auth/dependencies.py` provides `get_current_user` (decodes JWT `sub`, loads the user). Google OAuth is supported; `redirect_slashes=False` in `main.py` is deliberate to avoid a 307 on the OAuth callback.
- Role-based access: `learner`, `admin`, `super_admin` backed by `Role`/`Permission`/`RolePermission`/`UserRole`. Super-admins manage roles and subscriptions; normal admins get scoped reads (e.g. `payments.read`).
- `AdminRateLimitMiddleware` (`app/core/rate_limit.py`) rate-limits admin/login routes.
- Admin mutations are recorded to audit logs (`app/modules/admin/audit_service.py`). The `subscriptions/` module (billing) stores **only provider IDs** (masked in admin views) — never raw payment data.

## Frontend architecture

- **App Router** under `src/app/`. Route groups like `(auth)` and dynamic segments like `sessions/[sessionId]` are in use. Top-level pages include `dashboard`, `courses`, `sessions`, `task`, `challenges`, `diagnosis`, `stats`, `profile`, `settings`, plus marketing pages (`about`, `features`, `pricing`, `how-it-works`). Admin pages live under `src/app/admin/`.
- **API access**: one shared axios instance in `src/lib/api.ts`. It auto-attaches the JWT from `localStorage` and, on a `401` from a non-auth endpoint, clears the token and redirects to `/login`. Per-domain wrappers (`sessions-api.ts`, `auth-api.ts`, `challenges-api.ts`, `progress-api.ts`, `streak-api.ts`, `preferences-api.ts`, `subscriptions-api.ts`, `diagnosis-api.ts`, `tasks-api.ts`, `admin-api.ts`, …) build on it — add new calls to the matching `*-api.ts`, don't create new axios instances. Base URL comes from `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`).
- **Server state** via TanStack Query (`src/providers/query-provider.tsx`); domain hooks in `src/hooks/` (e.g. `useSessionsFlow`, `useNextTask`, `useSubmitResponse`, `useDiagnosis`, `useStreakDisplay`). **Client state** via Zustand stores in `src/store/` (`authStore`, `sessionStore`, `taskStore`, `diagnosisStore`, `streakDemoStore`).
- **Chat UI** is component-driven: `src/components/chat/` (`ChatUI.tsx`, `ChatChrome.tsx`, `orchestrator.tsx`) with `tasks/`, `feedback/`, `teaching/`, `evaluation/` subfolders and per-widget renderers. `runtimeMapping.tsx` / `runtimeReviewMapping.tsx` / `contractTaskAdapter.ts` map backend payloads to widgets. Backend widget keys are normalized to stable snake_case by `app/modules/sessions/widget_mapping.py` — keep that mapping in sync when adding task/widget types on either side.
- Other component areas: `src/components/{admin,auth,dashboard,sessions,streak,layout,ui}/`.
- `@/*` path alias maps to `src/*` (tsconfig). TypeScript `strict` is on.

## Conventions

- Backend: keep DB access in repositories, business logic + commits in services, and routes thin. Raise domain exceptions; translate to HTTP at the route boundary.
- New ORM model → register it in `app/models.py` and generate an Alembic migration.
- New activity *kind* → add an archetype to `app/scoring/archetypes.py` **and** a contract row in `app/modules/sessions/contracts/registry.py` (it will fail at import if you add one without the other).
- New task/widget type → update both the backend widget mapping and the corresponding `src/components/chat/` renderer.
- Scoring math is deterministic and lives only in `app/scoring/` — consume it, don't duplicate it. See `backend/RESTRUCTURE_DECISIONS.md` for the locked constants' rationale.
