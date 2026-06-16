# LingosAI Operations Runbook

> Phase 1 (Production Hardening) policy deliverables: environment separation,
> secrets strategy, database backup/restore, and migration policy. AWS-specific
> mechanics (Secrets Manager, RDS, ECS one-off tasks) land in Phase 3 — this
> document fixes the **policies** those mechanics must implement.
>
> ⚠️ `docs/` is git-ignored — this file is force-added (`git add -f docs/RUNBOOK.md`).
>
> Last updated: 2026-06-16.

---

## 1. Environment separation (plan 1.7)

Three environments, three configs. They differ in **secrets and origins**, not in code.

| | development | staging | production |
|---|---|---|---|
| `ENVIRONMENT` | `development` | **`production`** | `production` |
| Where | local laptop | AWS (prod-like) | AWS |
| Secrets / provider keys | local `.env`, test keys | own secrets, **test** keys | own secrets, **live** keys |
| `DEBUG` / `SQL_ECHO` | may be true | false | false |
| `DEV_OTP_BYPASS` | may be true | false | false |
| `AUTH_COOKIE_SECURE` | false (http) | true | true |
| `CORS_ORIGINS` | `http://localhost:3000` | `https://www-staging.lingosai.com` | `https://www.lingosai.com` |
| `LANGCHAIN_TRACING_V2` | optional (true ok) | off unless decided | off (see 1.12 in plan) |
| `STRICT_CONTRACTS` | **on** | **on** | **on** |

Key rule: **staging runs with `ENVIRONMENT=production`** so it exercises the same
fail-fast prod guard (`app/core/config.py::_guard_production`) as production. The
guard refuses to boot on unsafe combinations (DEBUG/SQL_ECHO/DEV_OTP_BYPASS on,
missing `OTP_HASHING_SECRET`, `AUTH_COOKIE_SECURE=false`, or localhost in
`CORS_ORIGINS`). A misconfigured prod boot should crash, not degrade.

`STRICT_CONTRACTS` stays **on in every environment** so archetype contract
violations surface loudly rather than in front of a learner.

---

## 2. Secrets strategy (plan 1.8)

**Never commit real secrets.** `.env` is git-ignored; `.env.production.example`
is the canonical key list (no values). Config flows through
`app/core/config.py` (`pydantic-settings`) reading the repo-root `.env`.

**Generate strong values:**
```bash
openssl rand -hex 32   # JWT_SECRET
openssl rand -hex 32   # OTP_HASHING_SECRET — MUST be distinct from JWT_SECRET
                       # (the prod guard rejects an empty OTP_HASHING_SECRET)
```

**In AWS (Phase 3):** every sensitive key becomes a **Secrets Manager** entry
(or SSM SecureString) and is injected into the ECS task definition via the
`secrets` block — the app reads them as ordinary env vars, no code change.
Non-secret config (`CORS_ORIGINS`, model names) can be plain task-def env / SSM
parameters.

**Secrets to store** (from `.env.production.example`): `DATABASE_URL`,
`REDIS_URL`, `JWT_SECRET`, `OTP_HASHING_SECRET`, `OPENAI_API_KEY`,
`PINECONE_API_KEY`, `AZURE_SPEECH_KEY`, `DEEPGRAM_API_KEY`,
`GOOGLE_CLIENT_ID/SECRET`, `RAZORPAY_KEY_ID/SECRET/WEBHOOK_SECRET`,
`SENTRY_DSN`, `LANGCHAIN_API_KEY`, `RESEND_API_KEY` (or SES via IAM role).

**Rotation:**
- `JWT_SECRET` — rotating **invalidates all existing access tokens** (and thus
  sessions). Do it in a maintenance window. Update Secrets Manager → redeploy.
- `OTP_HASHING_SECRET` — rotating invalidates outstanding OTPs (low blast
  radius; users just re-request). Update → redeploy.
- Provider keys (OpenAI/Pinecone/Azure/Deepgram/Razorpay/Google) — create the
  new key in the provider console, update Secrets Manager, redeploy, then revoke
  the old key once the new one is confirmed live.

---

## 3. Database backup & restore (plan 1.11)

**Automated (Phase 3 enables on RDS):** daily snapshots + point-in-time
recovery (PITR), **7-day** retention to start. A **monthly** manual snapshot is
retained longer (≈90 days) as a known-good restore point.

**Manual logical backup** (pre-migration safety net / local):
```bash
# Dump (custom format, compressed)
pg_dump "$DATABASE_URL" -Fc -f lingosai_$(date +%Y%m%d_%H%M).dump

# Restore into a clean database
createdb lingosai_restore
pg_restore -d "postgresql://.../lingosai_restore" --clean --if-exists lingosai_*.dump
```

**Restore drill — run once before launch** (an untested backup is not a backup):
restore the latest dump into a fresh database, point a local app at it, and
confirm login + a session loads. Targets: **RPO ≤ 5 min** (PITR), **RTO ≤ 1 hr**
(restore snapshot to new RDS, repoint `DATABASE_URL`, redeploy).

⚠️ **History-scrub prerequisite (audit E1):** `backup*.sql` dumps exist in git
history. If they ever held production data, treat it as a disclosure risk —
`git filter-repo` to purge and rotate any secrets they contained — **before**
the repo is made public. (Solo founder = low blast radius; coordinate + re-clone.)

---

## 4. Database migration policy (plan 1.13)

- **Migrations run as a one-off task, NEVER on container boot.** With N tasks,
  booting `alembic upgrade head` per container races the same migration. The
  prod process (`backend/scripts/start-prod.sh`) deliberately does **not** run
  migrations; Phase 3 adds a dedicated ECS one-off task (`alembic upgrade head`,
  same image) that `deploy.yml` runs **before** the service update.
- **Every ORM model must be registered in `app/models.py`** (per CLAUDE.md) so
  Alembic autogenerate discovers all tables via `Base.metadata`. Adding a model
  without registering it silently breaks migrations and relationships.
- **Snapshot before risky migrations:** snapshot RDS → run the one-off migration
  task → verify → on failure, restore the snapshot. Never run a destructive
  migration without a fresh snapshot.
- The app stores `DATABASE_URL` as plain `postgresql://…`; `app/core/database.py`
  rewrites it to `postgresql+psycopg://…`. Do not hardcode the driver.

---

## 5. Rate limiting baseline (plan 1.10 — verify)

Already in place; recorded here as the tuning baseline (tighten from
`ai_request_logs` per-user counts once there's real traffic):

- `AdminRateLimitMiddleware` (wired in `app/main.py`) — login 20/60s, admin
  300/60s, IP-keyed.
- AI per-user limits: `AI_RATE_LIMIT_PER_MINUTE=30`,
  `AI_RATE_LIMIT_TRANSCRIBE_PER_MINUTE=20`, `WS_MESSAGE_RATE_PER_MINUTE=20`,
  `WS_A2Z_STREAMS_PER_MINUTE=10`. Redis-backed when reachable (multi-worker safe
  on ElastiCache), in-memory fallback for dev/tests.
