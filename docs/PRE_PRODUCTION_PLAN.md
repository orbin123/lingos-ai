# LingosAI — Pre-Production Plan (Go-Live Roadmap)

> **Audience:** the coding agent (and humans) taking LingosAI from "green CI on a laptop" to
> "running live on AWS."
> **Companion docs:** [`ci-cd.md`](./ci-cd.md) · [`PRE_PRODUCTION_AUDIT.md`](./PRE_PRODUCTION_AUDIT.md) ·
> [`testing-strategy.md`](./testing-strategy.md).
> **Why this doc exists:** those three were each written at a different point and **all three now
> understate how far the work has progressed.** This doc reconciles them against the *verified*
> state of the tree (measured 2026-06-16, not assumed) and lays out exactly what remains.
> **Target platform:** **AWS ECS Fargate** (containers behind an ALB; RDS + ElastiCache; S3 +
> CloudFront for media).
> **Status of this doc:** the **CI/CD and test foundation are done**; remaining work is
> **containerization → AWS infra → a few P1 prod-code fixes → branch protection → runbook.**

> ⚠️ Parts of `docs/` are git-ignored. This file must be **force-added** (`git add -f
> docs/PRE_PRODUCTION_PLAN.md`) or it won't be tracked.

---

## 0. Status reconciliation — claimed vs. verified

What the prior docs say vs. what is actually on disk today. Evidence was read at the cited
location this session.

| Area | Prior-doc claim | **Verified actual state** | Evidence |
|---|---|---|---|
| Backend CI | "runs only 3 files; no mypy" (audit G1) | **DONE — full suite, blocking.** lint + `ruff format --check` + **mypy** + unit + integration + coverage `--cov-fail-under=73` | `.github/workflows/backend.yml`; commit `453cc11` (mypy → blocking) |
| Frontend CI | "none at all" (audit G2) | **DONE — blocking.** eslint + `tsc --noEmit` + Vitest+coverage + `next build` | `.github/workflows/frontend.yml` |
| Contract CI | Phase 3 "not yet executed" (ci-cd) | **DONE.** OpenAPI snapshot drift gate; `openapi.json` committed | `.github/workflows/contract.yml`; `backend/openapi.json` |
| Config dev/prod boundary | "weakest area; no boundary" (audit A1) | **DONE.** `@model_validator` prod guard, env CORS, `sql_echo`; both env templates exist | `backend/app/core/config.py:248-285`; `.env.example`, `.env.production.example` |
| Backend tests | red baseline / 3 files | **DONE.** 4594 passed, **75% cov**; split into `tests/unit` + `tests/integration` | `testing-strategy.md` §Session 4 |
| Frontend tests | "near-zero" (audit F2) | **PARTIAL.** Vitest stack + Phase 8 unit tests (17 files/94 tests); **Phase 9/10 not done** | `frontend/tests/`; `testing-strategy.md` §NEXT |
| Subscriptions layering | route-level DB writes (audit B1) | **DONE.** service + repository exist; routes thin | audit §Pass 1 |
| Frontend lockfile | "not committed" (audit G4) | **DONE.** `frontend/package-lock.json` tracked | repo root of `frontend/` |
| Debug scripts / DB dumps in index | tracked (audit E1/E2) | **DONE (index).** untracked + scripts deleted | audit §Pass 1 |
| **Dockerfiles** | "none exist" (audit G3) | **❌ NOT STARTED.** no backend/frontend Dockerfile, no `.dockerignore`, no prod compose | `find -iname Dockerfile` → none |
| **AWS infra** | not in scope of prior docs | **❌ NOT STARTED.** no IaC, no ECR/ECS/RDS, no deploy job | — |
| **Branch protection** | Phase 5 (ci-cd) | **❌ NOT STARTED.** no `CODEOWNERS`, no PR template, no required checks | `.github/` |
| **B4 concurrency guard** | P1 (audit B4) | **❌ STILL PRESENT.** module-global sets | `learning_session/service.py:112,116` |
| **D1/D2 OAuth** | P1 (audit) | **❌ NOT DONE.** optional `state`, JWT-in-URL | `auth/routes.py` |
| **git-history scrub (E1)** | owner action | **❌ OPEN.** `backup*.sql` still in history | commits `866e776`, `ea59f01`, `e8ab3ad` |
| **Deploy runbook (H1)** | P2 | **❌ NOT STARTED.** no `DEPLOY.md` | — |

---

## 1. Already production-ready ✅ (do not redo)

These are **closed**. Don't re-litigate them — point new work at the gaps in §2.

- **CI/CD pipeline** — four blocking GitHub Actions workflows (`backend`, `frontend`,
  `contract`, `backend-curriculum`). Every push/PR runs ruff lint+format, **mypy** (blocking),
  the full pytest suite behind a 73% coverage floor, the frontend lint/types/test/build, and
  an OpenAPI drift check. Actions are pinned, cached, least-privilege (`contents: read`),
  `concurrency` cancel-in-progress.
- **Dev/prod config boundary** — `config.py` refuses to boot under `ENVIRONMENT=production`
  when `DEBUG`/`SQL_ECHO`/`DEV_OTP_BYPASS` are on, `OTP_HASHING_SECRET` is unset,
  `AUTH_COOKIE_SECURE` is off, or `CORS_ORIGINS` is empty/localhost. CORS is env-driven and
  method/header-restricted. `.env.production.example` is the canonical prod key list.
- **Test foundation** — backend 4594 green @ 75% (`tests/unit` + `tests/integration`, shared
  fixtures/factories/mocks, the Complete Learning Loop); frontend Vitest+RTL+jsdom+MSW with
  Phase 8 unit tests.
- **Observability & contracts** — Sentry wired (`app/core/sentry.py`, no-op when DSN empty),
  `/health` liveness endpoint, committed `openapi.json` snapshot + drift gate.
- **Reproducibility** — backend `pyproject.toml` pins exact versions; `frontend/package-lock.json`
  committed; 36 alembic migrations.

---

## 2. Release-readiness gates (ordered roadmap to live)

### Phase A — Containerization 🟥 *critical path; nothing deploys without it*

| Artifact | What it does |
|---|---|
| `backend/Dockerfile` | Multi-stage on a `uv`-based Python 3.11 image: **builder** (`uv sync --frozen`) → **slim runtime**. Entrypoint runs `alembic upgrade head` (or delegated to a one-off task — see Phase C) then starts the server. |
| `frontend/Dockerfile` | Node 20 **builder** → slim runtime. Requires adding `output: "standalone"` to `frontend/next.config.ts` (not set today) so the runtime image ships only the standalone server + static assets. |
| `backend/.dockerignore`, `frontend/.dockerignore` | Exclude `.venv`, `node_modules`, `app/ai/**/_cache/`, `tests/`, `.env`, `.git`. |
| `compose.prod.yml` | app + Postgres + Redis for a **local prod-parity smoke test**. Distinct from the dev `docker-compose.yml`, which stays Postgres+Redis-only. |

Additional code items in this phase:
- **Production server** — only `uvicorn[standard]` is a dep today; **add `gunicorn` with
  `uvicorn.workers.UvicornWorker`**. ⚠️ **Worker count is gated on Phase B4** — until the
  concurrency guard is cross-process, run **a single worker** and state that loudly in the
  Dockerfile/compose comments.
- **Readiness probe** — `/health` (`backend/app/main.py:122`) is liveness-only (`{"status":
  "ok"}`). Add a `/health/ready` that checks DB + Redis connectivity for the ALB/ECS target
  group, so a task with a broken DB connection is pulled from rotation.

**Acceptance:** `docker compose -f compose.prod.yml up` boots the full stack locally; `/health`
and `/health/ready` return 200; the frontend renders against the containerized backend.

### Phase B — P1 prod-code hardening 🟥 *must precede multi-worker scaling & public traffic*

- **B4 — multi-worker concurrency guard.** `learning_session/service.py:112,116` use module
  globals (`_completing_daily_uuids`, `_pending_note_tasks`) to dedupe completions. These are
  **per-process** — under >1 worker the guard silently stops working and double-scoring becomes
  possible. **Fix:** make the DB unique constraint the source of truth (catch the integrity
  error) or take a short Redis lock (Redis is already in the stack). **Until then, pin a single
  worker.** This is the textbook "works in dev, fails invisibly under load" item from the audit.
- **D1 — OAuth `state` is optional** (`auth/routes.py` ~`:667`, `:715`); a forged callback is
  accepted (login CSRF). Require + validate `state` on the login path.
- **D2 — JWT in redirect URL query string** (`auth/routes.py:775`); tokens leak via proxy logs,
  browser history, and `Referer`. Switch to a short-lived single-use code exchange or an
  HttpOnly secure cookie.
- **F1 — duplicated API base URL.** `NEXT_PUBLIC_API_URL || "http://localhost:8000"` is repeated
  across ~10 frontend files; a prod misconfig surfaces inconsistently. Centralize in
  `src/lib/api-config.ts` and import everywhere.

**P2 — schedule post-launch (list, don't block):** D3 (remove OTP-pepper→JWT fallback), D4
(server-side password rules), D5 (log `user.id` not email), C1/C2 (narrow broad `except`), F3–F6
(non-null assertions, fetch zod validation, query error states, strip `console.error`), G5
(pre-commit hooks), G6 (restore ESLint React-Compiler rules to `error`).

### Phase C — AWS infrastructure (ECS Fargate) 🟥

Reference architecture to stand up (IaC tool chosen in §4):

- **ECR** — two repositories (`lingosai-backend`, `lingosai-frontend`); images built + pushed by CD.
- **ECS Fargate** — a backend service and a frontend service behind a shared **ALB** with
  host/path routing; task definitions reference the ECR images; start at 1 task each,
  autoscaling later.
- **RDS PostgreSQL** — `app/core/database.py` already rewrites `postgresql://` → `postgresql+psycopg://`,
  so feed it the plain RDS URL. **ElastiCache Redis** for rate-limiting + the B4 lock.
  Security groups: only ECS tasks may reach RDS/Redis.
- **S3 + CloudFront for generated media** ⚠️ *real code item, not just infra.* TTS/STT/imagegen/
  pronunciation output is written to **local disk** by `LocalBlobStorage`
  (`app/ai/storage/local_client.py`) and served via `StaticFiles`. That does **not** survive
  Fargate's ephemeral filesystem or >1 task. Add an `S3BlobStorage` implementing the existing
  `app/ai/storage/interface.py`, select it by env in prod, and serve via CloudFront. The
  `*_CACHE_DIR` / `*_PUBLIC_URL_PREFIX` env keys become S3 bucket + CDN prefixes.
- **Secrets** — SSM Parameter Store / Secrets Manager → injected as task env. The `config.py`
  prod guard already fails-fast on unsafe/missing values, so a misconfigured secret crashes on
  boot (intended). Map every key in `.env.production.example` to a parameter — notably
  `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET`, `OTP_HASHING_SECRET`, `OPENAI_API_KEY`,
  `PINECONE_*`, `AZURE_SPEECH_*`, `GOOGLE_CLIENT_*`, `RAZORPAY_*`, `SENTRY_DSN`, `CORS_ORIGINS`.
- **Migrations** — run `alembic upgrade head` as a **one-off ECS task** (preferred over baking
  into every container start, so N tasks don't race the migration). Document the rollback story.
- **Logging** — ECS → CloudWatch Logs (`LOG_LEVEL` env already exists); Sentry DSN via secret;
  resolve `LANGCHAIN_TRACING_V2` per A5 below.

### Phase D — CD: build & deploy pipeline 🟥

- New `.github/workflows/deploy.yml`, triggered on `main` **after** the existing required checks
  pass: build both images → push to ECR → register new task definitions → `aws ecs
  update-service` (rolling deploy) → run the migration task. Authenticate via **GitHub OIDC role
  assumption** — no long-lived AWS keys in secrets. Ship non-blocking first, then make required.

### Phase E — Branch protection & repo governance 🟧 *(ci-cd.md Phase 5, still open)*

- Add `.github/CODEOWNERS` and `.github/pull_request_template.md` (neither exists).
- Branch protection on `main` (a repo *setting*, not a file — run via `gh` or the UI; cannot be
  set from this session). Required checks must match the job names:
  ```bash
  gh api -X PUT repos/:owner/:repo/branches/main/protection \
    -F 'required_status_checks.contexts[]=lint' \
    -F 'required_status_checks.contexts[]=types' \
    -F 'required_status_checks.contexts[]=unit' \
    -F 'required_status_checks.contexts[]=integration' \
    -F 'required_status_checks.contexts[]=coverage' \
    -F 'required_status_checks.contexts[]=ci' \
    -F 'required_status_checks.contexts[]=openapi-drift' \
    -F required_pull_request_reviews.required_approving_review_count=1 \
    -F enforce_admins=true -F restrictions=
  ```
- Optional: ci-cd.md Phase 4 coverage job-summary step (append a table to `$GITHUB_STEP_SUMMARY`).

### Phase F — Owner-only actions 🟧 *(cannot be done in code)*

- **E1 git-history scrub.** `backup.sql` / `backup_pre_phase8.sql` are untracked from the index
  but **remain in history** (verified in `866e776`, `ea59f01`, `e8ab3ad`). If they ever held
  production data, treat their presence as a disclosure incident: `git filter-repo` to purge,
  then rotate any secrets they contained. **Decide before the repo/app is public.**
- **A5 LangSmith data-residency.** `LANGCHAIN_TRACING_V2` ships **off** in the prod template.
  Confirm whether learner content may go off-platform and document retention before enabling.
- **Populate real prod env** per `.env.production.example` (live OpenAI/Pinecone/Azure/Google
  keys, **Razorpay prod keys**, `OTP_HASHING_SECRET`, prod `CORS_ORIGINS`, etc.).

### Phase G — Docs & remaining tests 🟩 *(parallelizable, not launch-blocking)*

- **`DEPLOY.md` runbook** — env per environment, the migration step, image build/run commands,
  post-deploy smoke check. Must live outside the gitignored part of `docs/` or be force-added.
- **Frontend testing Phase 9 + 10** — integration flows + zod contract tests (quality, not a
  hard gate). See `testing-strategy.md` §"NEXT SESSION" for the exact plan.

---

## 3. Critical path & sequencing

```
A (containers + readiness probe)
   └─> B4 single-worker pin  +  D1/D2 OAuth  +  F1 API config
          └─> C (ECR · Fargate+ALB · RDS · ElastiCache · S3/CloudFront · secrets · migration task)
                 └─> D (deploy.yml via OIDC)
                        └─> E (CODEOWNERS · PR template · branch protection)
                               └─> F (history scrub · LangSmith · real prod env)
                                      └─> flip backend to multi-worker once B4 is cross-process
```

**Minimum to point a domain at it (P0/P1 only):** Phase A containers, B4 pinned single-worker +
D1/D2, Phase C infra incl. **S3 media** and secrets, the Phase F owner actions. Branch
protection (E), multi-worker, and Phase G docs/tests can follow the first live deploy.

---

## 4. Open decisions for the user

- **IaC tool** — Terraform vs. AWS CDK. *(Recommend Terraform for portability; CDK if you prefer
  TypeScript parity with the frontend.)*
- **DNS/TLS** — Route 53 + ACM certificate on the ALB? Domain name?
- **Region & topology** — single-region to start (recommended) vs. multi-AZ-only vs. multi-region.
- **Frontend hosting long-term** — keep Next.js on ECS (this plan) or move to Amplify/Vercel later
  and reserve ECS for the API only.
- **Background work** — `_pending_note_tasks` are in-process asyncio tasks; decide whether RAG
  mentor-note generation moves to a worker/queue (Celery/SQS) before scaling out.

---

*State verified against the working tree on 2026-06-16. The CI/CD and test-foundation rows in §0
were confirmed by reading the on-disk workflow files and `config.py`; the "not started" rows were
confirmed by their absence (`find -iname Dockerfile`, missing `.github/CODEOWNERS`, B4 globals
still at `service.py:112,116`).*
