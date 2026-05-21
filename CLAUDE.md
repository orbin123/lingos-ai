# CLAUDE.md

Operating manual for Claude Code (and other AI agents) working in this repo.
Read this at the start of every session. If something here disagrees with
the code, trust the code and update this file.

---

## 1. Project Identity

**LingosAI / AI English Coach** — an AI-powered English coaching platform for
non-native speakers who want career-ready communication skills.

It is **not** a generic chat-with-AI app. The product loop is:

- Diagnose weaknesses through a structured diagnosis flow.
- Build a learner profile (level, goals, weak sub-skills, preferences).
- Serve a **stable, week-by-week curriculum** of daily activities.
- Personalize wording/topic of each activity with AI inside fixed slots.
- Evaluate every response with specific, corrective feedback — never
  generic "good job".
- Update a deterministic, weighted score → tier → reward → progress / streak.

Design philosophy:
- **Curriculum structure is fixed. AI personalizes inside controlled slots.**
- **Scoring is deterministic.** AI proposes raw scores; math is pure code.
- **Feedback must be corrective and tied to the user's actual mistakes.**

---

## 2. Tech Stack (verified)

**Backend** — `backend/` (Python 3.11+, managed by `uv`)
- FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2 + `pydantic-settings`
- PostgreSQL (psycopg 3) via `DATABASE_URL`
- Auth: `python-jose` JWT, `bcrypt`/`passlib`
- AI: `openai`, `langchain`, `langchain-openai`, `langgraph`, `langsmith`
- Speech: OpenAI TTS / Whisper STT, Azure Cognitive Services pronunciation
- Vectors: `pinecone` (verify runtime use before relying on it)
- Tests: `pytest`, `pytest-asyncio`. Lint: `ruff`. Types: `mypy`.

**Frontend** — `frontend/` (Node, npm)
- Next.js 16 (App Router), React 19, TypeScript 5
- TanStack Query, Zustand (`authStore`, `sessionStore`, `diagnosisStore`), Axios
- React Hook Form + Zod, Tailwind v4
- Tests: `node --test` (only `tests/admin-access.test.mjs` exists today).

**Infra** — `docker-compose.yml` at root for Postgres/Redis dev deps.
Redis is referenced in env, but **no Celery/queue worker is wired** in
`app/main.py`. Background jobs: **needs verification before use.**

**WebSockets** — _Needs verification._ `app/main.py` registers only REST
routers. The active session flow is REST (`/api/sessions/...`). Treat any
"streaming chat" as not yet implemented unless you confirm it.

---

## 3. Repository Map

```
ai-english-tutor/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry, router wiring, static mounts
│   │   ├── models.py            # Cross-module SQLAlchemy re-exports
│   │   ├── core/                # config, database, security (JWT), rate_limit
│   │   ├── scoring/             # PURE deterministic scoring (engine/archetypes/constants)
│   │   ├── ai/
│   │   │   ├── routes.py        # AI-facing endpoints
│   │   │   ├── agents/          # diagnosis + IELTS challenge agents, prompt_loader
│   │   │   ├── sessions/        # llm_evaluator, llm_feedback, llm_task_generator, factory
│   │   │   ├── llm/ embeddings/ tts/ stt/ pronunciation/ imagegen/ storage/
│   │   │   └── graphs/          # placeholder — empty today
│   │   ├── modules/
│   │   │   ├── auth/            # JWT login/register, Google OAuth callback
│   │   │   ├── admin/           # admin API, roles, audit, billing views
│   │   │   ├── diagnosis/       # diagnosis routes/service/evaluators/scoring
│   │   │   ├── curriculum/      # v1 + v2 models/repositories (v2 in transition)
│   │   │   ├── sessions/        # DAILY-SESSION core: planner, service, evaluator,
│   │   │   │                    # feedback_generator, task_generator, scoring_writer
│   │   │   ├── tasks/ skills/   # activity catalog + skill/sub-skill registry
│   │   │   ├── progress/ streaks/  # per-skill progress + streak counters
│   │   │   ├── responses/       # learner response storage
│   │   │   ├── learning_session/# older session module — verify before editing
│   │   │   ├── personalization/ preferences/   # learner profile + toggles
│   │   │   ├── subscriptions/   # billing + users router
│   │   │   └── challenges/      # IELTS-style standalone challenges
│   │   └── data/                # seed/static data
│   ├── alembic/versions/        # migrations (squashed initial + phase1..phase8)
│   ├── tests/                   # pytest suite
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next routes: (auth), dashboard, diagnosis,
│   │   │                        #   sessions, challenges, admin, profile, settings…
│   │   ├── components/          # auth, sessions, dashboard, streak, admin, layout
│   │   ├── hooks/               # useDiagnosis, useSessionsFlow, auth hooks
│   │   ├── lib/                 # api clients (sessions, diagnosis, progress, …)
│   │   ├── store/               # zustand stores
│   │   └── providers/
│   └── tests/admin-access.test.mjs
├── MD_FILES/
│   ├── PROJECT_INTERNAL_MAP.md       # internal architecture map
│   └── RESTRUCTURE_DECISIONS.md      # SOURCE OF TRUTH for scoring math (§1–§3)
├── docker-compose.yml
├── .env / .env.example
└── AGENTS.md                          # short version for Codex-style agents
```

---

## 4. Core Product Loop

1. **Diagnosis** — `modules/diagnosis` + `ai/agents/diagnosis_feedback.py`
   produce a learner profile and weak sub-skills.
2. **Curriculum** — `modules/curriculum` (v1 → v2) + `tasks/` + `skills/`.
   Fixed week/day plan driven by course length (24w / 48w) and enrollment.
3. **Session start** — `sessions/routes.py::start` calls `planner.py`,
   which resolves today's day from `UserEnrollment`, filters by
   `allow_reading/writing/speaking/listening`, and creates a `DailySession`.
4. **Activity delivery** — `task_generator` (LLM) personalizes copy inside
   a template slot. Templates + skill weights stay fixed.
5. **User submission** — `POST /api/sessions/{id}/activities/{...}/submit`.
6. **Evaluation** — `sessions/evaluator.py` calls `ai/sessions/llm_evaluator.py`;
   returns a structured score + mistakes list.
7. **Feedback** — `sessions/feedback_generator.py` produces corrective,
   mistake-linked feedback (no generic praise).
8. **Scoring** — `scoring/engine.py` (pure): raw_score → tier →
   base_reward → per-sub-skill distribution via the activity's archetype.
9. **Persistence** — `scoring_writer.py` writes per-skill points;
   `progress/` and `streaks/` feed the dashboard.

---

## 5. Architecture Rules

- Preserve layering: `routes → service → repository → models`, with Pydantic
  `schemas.py` per module.
- **Scoring math is pure.** No I/O, randomness, or DB calls in `app/scoring/`.
- **AI proposes, code decides.** LLMs return `raw_score` + mistakes;
  tiers / rewards / aggregation belong to `scoring/engine.py`.
- No business logic in React components — push it into `lib/*-api.ts`,
  hooks, or stores.
- Repositories do DB ops; services orchestrate; routes translate HTTP.
- Prefer small, testable diffs. Don't rewrite modules en bloc.
- **Curriculum v2 is in transition** (`v2_models.py`, `v2_repository.py`,
  migrations `d9e0f1a2b345`, `e4f5a6b7c890`, `e7f8a0b1c2d3`). Confirm which
  version a route uses before editing.

---

## 6. Agentic Development Workflow

1. Restate the request in 1–2 lines.
2. Open the related files (`Read`, `Grep`, or `Explore` agent for wide search).
3. Summarize current behavior before proposing changes.
4. List the exact files to be modified.
5. Produce a short plan (use `Plan` mode for non-trivial work).
6. Implement the **smallest** safe change.
7. Run the relevant tests / lint / typecheck (see §13).
8. Close with: files changed, checks run, risks, next step.

---

## 7. Safety Rules

- Don't delete files without an explicit reason in the response.
- Don't edit existing Alembic migrations. Add a new revision.
- Don't change DB schema without a migration **and** a rollback note.
- Don't break existing API response shapes — add fields additively or
  version a new endpoint.
- Don't change `scoring/` formulas without auditing every consumer
  (`progress/`, `streaks/`, dashboard, `scoring_writer.py`).
- Don't fake/skip tests. Don't mark work done while checks fail.
- Don't hardcode secrets. Use `app/core/config.py` + `.env`.
- Don't invent env vars without updating `.env.example` and `core/config.py`.
- Don't disable hooks/CI to land a change.

---

## 8. Feature Implementation Rules

When the feature spans both ends, work in this order:

1. Backend model + Alembic migration (if schema changes).
2. Repository → Service → Schemas.
3. Route (with auth dependency).
4. Backend test (happy path + at least one edge case).
5. Frontend API client (`src/lib/*-api.ts`) + types.
6. Hook (`src/hooks/`, TanStack Query pattern already in use).
7. UI in `src/app/...` or `src/components/...`.
8. Update docs (`AGENTS.md` / this file) if behavior or contracts change.

---

## 9. AI / LLM Rules

- All LLM calls live under `app/ai/`. Routes/services must not call OpenAI
  directly.
- Use structured output (JSON / Pydantic) whenever the result feeds code.
- Evaluation must return a **mistakes list with specific spans / reasons**.
  Feedback prompts consume that list — never produce free-form praise.
- Keep generation, evaluation, and scoring in **separate** components.
  The same call must not grade and reward.
- LLMs only supply `raw_score` and mistake metadata; `scoring/engine.py`
  decides tiers and rewards.
- LangSmith tracing defaults on (`LANGCHAIN_TRACING_V2=true`) — don't
  silently disable it.
- TTS / STT / image artifacts must go through the existing
  `LocalBlobStorage` cache pattern with their `*_CACHE_DIR` envs.

---

## 10. Curriculum & Personalization Rules

- The curriculum tree (course → week → day → planned activities) is
  **stable per course length** (24w / 48w). Do not regenerate it per user.
- AI personalizes only: topic, surface wording, examples, difficulty nudges
  — **inside** the slot defined by template + archetype.
- A user's level, goal, weak sub-skills, and `preferences` (in
  `modules/preferences` + `personalization`) feed personalization.
- Activity archetypes (`scoring/archetypes.py`) target one or more
  sub-skills with weight maps that must sum to 1.0. Don't change weights
  without updating tests and `RESTRUCTURE_DECISIONS.md`.

---

## 11. Chat / WebSocket Rules

- **No live WebSocket layer is wired in `app/main.py` today.** Session
  flow is REST: `start → next-activity → submit → scorecard`.
- If you add streaming, put transport code under `app/ai/` or a new
  `app/realtime/` module — never inside route handlers.
- Session state is server-authoritative (`DailySession` + attempts in DB).
  The client mirrors it via `sessionStore` + TanStack Query.
- Evaluation + scoring must stay server-side. The client must never
  compute scores.

---

## 12. Database & Migrations

- Migrations live in `backend/alembic/versions/`. Recent heads include
  `f2a3b4c5d6e7` (week-id repair) and `e7f8a0b1c2d3` (phase 8 drops).
- Commands:
  ```bash
  cd backend
  uv run alembic upgrade head
  uv run alembic downgrade -1            # local only, only if data-safe
  uv run alembic revision -m "msg" --autogenerate
  ```
- **Never** edit a migration that has run in any shared DB — add a new one.
- Important tables (non-exhaustive): users, roles/permissions, courses,
  curriculum_weeks/days, user_enrollments, daily_sessions, attempts,
  skills/sub_skills, progress, streaks, challenges, subscriptions, audits.
- `backup_pre_phase8.sql` is a snapshot — keep it. `backup.sql` is empty;
  don't rely on it.

---

## 13. Commands

**Backend** (from `backend/`):
```bash
uv sync                                  # install deps
uv run uvicorn app.main:app --reload     # dev server
uv run alembic upgrade head              # apply migrations
uv run pytest                            # all tests
uv run pytest tests/test_scoring_engine.py -k tier   # focused
uv run ruff check app tests              # lint
uv run ruff format app tests             # format
uv run mypy app                          # types — verify config first
```

**Frontend** (from `frontend/`):
```bash
npm install
npm run dev            # next dev
npm run build          # next build
npm run lint           # eslint
npm run test:admin     # node --test tests/admin-access.test.mjs (only suite)
npx tsc --noEmit       # typecheck — no script defined yet (TODO add one)
```

**Docker dev deps**:
```bash
docker compose up -d   # Postgres, Redis — verify services in docker-compose.yml
```

---

## 14. Common Failure / Risk Areas (observed)

- **Curriculum v1 ↔ v2 split.** `curriculum/models.py` and
  `curriculum/v2_models.py` coexist; recent uncommitted edits touch both.
  Always confirm which set a route uses.
- **`sessions/` vs `learning_session/`.** Active module is `sessions/`.
  `learning_session/` may be legacy — verify before editing.
- **`ai/graphs/` is empty** despite the `langgraph` dependency.
- **No WebSocket layer** even though docs/PRs may imply streaming.
- **Frontend test coverage is thin** (one admin-access test). Don't trust
  "frontend tests pass" as a quality signal.
- **Scoring is tightly coupled** to dashboard/progress/streaks. Any change
  to `scoring/engine.py` or archetype weights ripples through these.
- **Active branch `refactor/new-core-loop-backend`** has uncommitted edits
  in `curriculum/`, `sessions/routes.py`, and `useSessionsFlow.ts` — check
  `git status` before large changes.
- **Pinecone, Celery, Redis** are referenced but their runtime wiring needs
  verification before relying on them.

---

## 15. Definition of Done

A task is done **only** when ALL hold:

- Implementation matches the request — no scope creep, no half-finished code.
- Existing behavior / API shapes preserved (or migration documented).
- Backend: `pytest` + `ruff check` pass on touched paths.
- Frontend: `next build` + `eslint` pass on touched paths.
- New behavior has at least one test, or the gap is explicitly called out.
- Final reply lists: files changed, checks run, risks, next step.
- Docs (`CLAUDE.md` / `AGENTS.md`) updated if behavior or contracts changed.

---

## 16. Session Closing Checklist

End every session with:

- **Summary** — one paragraph of what changed and why.
- **Files changed** — bullet list (markdown links to paths).
- **Tests / checks run** — exact commands + pass/fail.
- **Known issues** — anything unverified or skipped.
- **Suggested next step** — the smallest next move.
- **Docs sync** — whether `CLAUDE.md` / `AGENTS.md` needs updating, and
  if so, do it in the same session.

---
