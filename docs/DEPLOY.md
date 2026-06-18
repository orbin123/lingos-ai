# DEPLOY.md — Build, Artifact & Deployment Workflow

> Companion to [`complete_production_plan.md`](./complete_production_plan.md) (Phase 2) and
> [`RUNBOOK.md`](./RUNBOOK.md) (operations). This file documents how code becomes a running
> deployment. Phase 2 ships the **build + artifact** half (container image, CI gate, governance);
> the AWS **deploy** half (`deploy.yml` → ECR/ECS) is wired in Phase 3 — the contract it must
> satisfy is specified here so Phase 3 has nothing to invent.

---

## 1. The container image

The backend ships as a single multi-stage image built from [`backend/Dockerfile`](../backend/Dockerfile):

- **Builder:** `uv`-based, installs the frozen lockfile (`uv sync --frozen --no-dev`), compiles
  bytecode.
- **Runtime:** `python:3.11-slim`, non-root `appuser` (uid 10001), only the venv + app code, no
  build toolchain. Base images pinned by **index digest** for cross-arch reproducibility.
- **Entrypoint:** gunicorn + `UvicornWorker` (mirrors `backend/scripts/start-prod.sh`).
  `WEB_CONCURRENCY` defaults to `1`.
- **Migrations are NOT in the image entrypoint** — they run as a separate one-off step
  (`alembic upgrade head`) so concurrent tasks never race the same migration.

Build & smoke-test locally:

```bash
docker build -f backend/Dockerfile -t lingosai-backend:test backend
docker compose -f compose.prod.yml up --build   # migrate -> backend + postgres + redis
curl -fsS localhost:8000/health/ready           # 200 = DB + Redis healthy
docker compose -f compose.prod.yml down
```

The frontend has **no image** — it deploys to Vercel (AD-1).

---

## 2. Image tagging, versioning & rollback

> Implemented in `deploy.yml` (Phase 3). This section matches what that workflow actually does.

**Registry:** Amazon ECR, repo `lingosai-backend` (one repo; frontend has none). The repo is
configured for **immutable tags**.

**Every build pushes exactly one tag** — the immutable `git-<short-sha>`:

| Tag | Example | Purpose |
|---|---|---|
| `git-<short-sha>` | `git-9add7b5` | **Immutable identity** — the only tag pushed, and the only thing you ever deploy. |

A moving `:latest` or daily `vYYYY.MM.DD` tag was considered but **not** used: an immutable repo
rejects overwriting a tag, so a moving tag would fail every redeploy. Deploy-by-sha is exact and
reproducible by construction.

**Rollback** is automatic on smoke failure: `deploy.yml` snapshots the running task-def before the
rolling update and re-points the service at it if `/health/ready` fails. To roll back manually:

```bash
# Backend — re-point the ECS service at the previous task-definition revision
# (which references the previous image sha). Instant and safe because images
# are immutable by sha.
aws ecs update-service \
  --cluster <cluster> --service <service> \
  --task-definition <family>:<previous-revision>

# Frontend — Vercel dashboard → Deployments → previous → "Promote to Production".
```

ECS keeps prior task-definition revisions, so rollback is a pointer change, not a rebuild.
**Migrations are forward-only** — a service rollback does not revert an applied migration.

---

## 3. Branching & deployment workflow

```
main (protected, always deployable)
  └── feature/<short-name>  ──► open PR
            │
            ├─ CI: lint · types · unit · integration · coverage · contract · frontend · docker-build
            ├─ Vercel posts a Preview deploy URL for manual QA
            ├─ CODEOWNERS review + all green checks required
            ▼
        squash-merge to main  ──►  Phase 3 deploy.yml: build → ECR → migrate → ECS rolling → smoke
                                    Vercel: auto-deploys frontend to production
```

- **One protected branch (`main`)** + short-lived `feature/*` branches. Staging is an *environment*,
  not a branch — deploy any sha to staging via `workflow_dispatch` (Phase 3).
- **Squash-merge** so `main` stays linear and each merge = one deployable unit.

### CI gates (all blocking, exist today + new in Phase 2)

| Check (status context) | Workflow | Added |
|---|---|---|
| `lint`, `types`, `unit`, `integration`, `coverage` | `backend.yml` | Phase 0 |
| `ci` (eslint + tsc + vitest + next build) | `frontend.yml` | Phase 0 |
| `openapi-drift` | `contract.yml` | Phase 0 |
| `docker-build` (image build + Trivy HIGH/CRITICAL) | `docker.yml` | **Phase 2** |

---

## 4. Frontend deployment model (Vercel — AD-1)

- Connect the GitHub repo to Vercel; **Root Directory = `frontend/`**.
- **Production branch = `main`** → `https://www.lingosai.com` (domain in Phase 4). A merge to `main`
  triggers a Vercel production deploy **and** the backend `deploy.yml` (push trigger) on the same
  commit — the FE/BE lockstep (G1.5). No coupling between them beyond the shared commit.
- **Preview deploys** on every PR (ephemeral URLs) — the manual QA surface.
- Build command `next build`; Vercel owns CDN, TLS, image optimization. **No Dockerfile.**
- Env vars in Vercel, scoped Production / Preview / Development:
  - `NEXT_PUBLIC_API_URL` → `https://api.lingosai.com` (Prod) /
    `https://api-staging.lingosai.com` (Preview) / `http://localhost:8000` (Dev).

---

## 5. Branch protection (repo setting — run once)

Enable after the first PR has reported the new `docker-build` check at least once, so the context
name exists:

```bash
gh api -X PUT repos/orbin123/lingos-ai/branches/main/protection \
  -F 'required_status_checks.strict=true' \
  -F 'required_status_checks.contexts[]=lint' \
  -F 'required_status_checks.contexts[]=types' \
  -F 'required_status_checks.contexts[]=unit' \
  -F 'required_status_checks.contexts[]=integration' \
  -F 'required_status_checks.contexts[]=coverage' \
  -F 'required_status_checks.contexts[]=ci' \
  -F 'required_status_checks.contexts[]=openapi-drift' \
  -F 'required_status_checks.contexts[]=docker-build' \
  -F 'required_pull_request_reviews.required_approving_review_count=1' \
  -F 'enforce_admins=true' -F 'restrictions='
```

Contexts must match job names exactly (they do).

---

## 6. What `deploy.yml` does (as implemented)

1. **Trigger:** automatic on **push to `main`** (auto-deploys production); `workflow_dispatch` also
   supports a manual run targeting `staging` or `production` for replays/staging.
2. **AWS auth:** assume a role via **GitHub OIDC** — no long-lived AWS keys in GitHub secrets. Scope
   the role to ECR push + ECS update + `iam:PassRole` for the task roles only.
3. **Build & push:** build `backend/Dockerfile`, push to ECR with the single immutable `git-<sha>`
   tag from §2.
4. **Migrate:** run the one-off migration task (same image, `alembic upgrade head`) and **wait for
   success** before touching the service. On failure, abort — old tasks keep serving.
5. **Deploy:** snapshot the running task-def (rollback target), register a new task-definition
   revision (new image sha) → `aws ecs update-service` (rolling, zero downtime) → wait for stable.
6. **Smoke + auto-rollback:** hit `/health/ready`; on failure, automatically re-point the service at
   the snapshotted task-def, wait stable, and fail the job (per §2).

Also created in Phase 3: the ECR repo, the OIDC role, and the ECS cluster/service/task definitions
(Terraform). `S3BlobStorage` (replacing local-disk media so the container is stateless) is the one
real code item that Phase-3 deploy depends on — see plan §3.5.
