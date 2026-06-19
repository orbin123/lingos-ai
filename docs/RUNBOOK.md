# LingosAI Operations Runbook

> **§§1–5 (Phase 1)** are the *policy* deliverables: environment separation,
> secrets strategy, database backup/restore, and migration policy.
> **§§6–11 (Phase 5)** are the *operational* runbooks now that AWS is live:
> monitoring/alerting, incident response, deploy & rollback, secret rotation,
> weekly/monthly maintenance, and scaling triggers. Commands use the real
> production resource names (region **us-east-1**).
>
> ⚠️ `docs/` is git-ignored — this file is force-added (`git add -f docs/RUNBOOK.md`).
>
> Last updated: 2026-06-17.

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

**Restore drill — run periodically** (an untested backup is not a backup).
Targets: **RPO ≤ 5 min** (PITR), **RTO ≤ 1 hr** (restore snapshot → new RDS →
repoint `DATABASE_URL` → redeploy).

The RDS-snapshot drill (matches how a real recovery works):
```bash
# 1. latest automated snapshot
aws rds describe-db-snapshots --region us-east-1 --snapshot-type automated \
  --query "reverse(sort_by(DBSnapshots[?DBInstanceIdentifier=='lingosai-production-postgres'],&SnapshotCreateTime))[0].DBSnapshotIdentifier" --output text
# 2. restore to a throwaway instance (private, single-AZ), reusing prod subnet group + SG
aws rds restore-db-instance-from-db-snapshot --db-instance-identifier lingosai-restore-drill \
  --db-snapshot-identifier "<snapshot>" --db-instance-class db.t4g.small --no-multi-az \
  --no-publicly-accessible --db-subnet-group-name lingosai-production-db-subnets \
  --vpc-security-group-ids sg-04f4eb40d803afb93 --region us-east-1
aws rds wait db-instance-available --db-instance-identifier lingosai-restore-drill --region us-east-1
# 3. tear down (no final snapshot — it's a throwaway)
aws rds delete-db-instance --db-instance-identifier lingosai-restore-drill \
  --skip-final-snapshot --delete-automated-backups --region us-east-1
```
> **Data-integrity check (do this hands-on — never put the prod password in a
> file/env override):** while the drill instance is up, verify row-level data via
> **ECS Exec** into a running task (`aws ecs execute-command … --command
> "python -c '…psycopg count…'"` with `DATABASE_URL` pointing at the drill
> endpoint) or `psql` from a bastion in the VPC. The drill instance is private by
> design, so verification happens inside the VPC.

**Last drill — 2026-06-18:** snapshot `rds:lingosai-production-postgres-2026-06-18-03-06`
restored to `lingosai-restore-drill`; **available in 7m 28s** (well within the 1 hr
RTO), engine 16.4 / 20 GB matched prod; instance torn down. Row-level data check
deferred to a hands-on run (credential safety).

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

---

## 6. Monitoring & alerting (plan 5.1)

One on-call (the founder), reached by **email via SNS topic
`lingosai-production-alerts`** (→ `orbinsunny9495@gmail.com`). Confirm the SNS
email subscription shows **Confirmed** (click the AWS confirmation email once).

**CloudWatch alarms** (Terraform `modules/observability`) — high-signal only;
everything else lives on dashboards to avoid alert fatigue:

| Alarm | Fires when | First move |
|---|---|---|
| `lingosai-production-alb-5xx` | >10 target 5xx/min for 2 min | Sentry + ECS logs; likely app/dependency failure → consider rollback (§8) |
| `lingosai-production-alb-unhealthy-hosts` | a target fails `/health/ready` | check `/health/ready` breakdown (db/redis); check ECS task health |
| `lingosai-production-ecs-cpu-high` | CPU >85% for 3 min | scale task count (§11) |
| `lingosai-production-rds-cpu-high` | RDS CPU >85% for 3 min | slow queries; watch t-class CPU credits |
| `lingosai-production-rds-free-storage-low` | free storage <2 GiB | autoscaling should cover; investigate growth |
| `lingosai-production-rds-cpu-credits-low` | t-class CPU credit balance <50 | sustained CPU will throttle; consider larger class |
| `lingosai-production-rds-connections-high` | avg connections >100 for 3 min | possible leak; consider pooling (RDS Proxy/PgBouncer) |
| `lingosai-production-ecs-memory-high` | memory >85% for 3 min | OOM-kill risk; bump task memory or scale out |
| `lingosai-production-redis-memory-high` | memory >85% for 3 min | rate-limit/lock keys may evict; bump node size |
| `lingosai-production-redis-evictions` | any evictions over 10 min | memory pressure dropping keys; bump node size |

**Synthetic uptime:** Route53 health check `lingosai-production-uptime-health`
hits `https://api.lingosai.com/health` every 30s from multiple AWS regions →
alarm `lingosai-production-uptime-health` pages via SNS if it fails. Uses
`/health` (liveness), not `/health/ready`.

**Cost:** AWS Budget `lingosai-production-monthly-cost` (**$150/mo**) emails at
80% actual + 100% forecasted spend.

**Errors:** Sentry — **backend + frontend** (`@sentry/nextjs`) both wired
(`tracesSampleRate=0.1`, no-op when DSN empty). Set **`NEXT_PUBLIC_SENTRY_DSN`**
in Vercel (Production + Preview); optionally `SENTRY_AUTH_TOKEN` / `SENTRY_ORG` /
`SENTRY_PROJECT` for source-map upload at build. **AI metrics:** `ai_request_logs`
(latency/tokens/status) + the **AI-cost dashboard** at `/admin/ai-costs`
(`ai_costs.read`): spend by capability/model + daily trend, derived from the LLM
pricing table. **LangSmith:** off (data-residency, plan 1.12).

**Known gaps (TODO):** NAT-gateway error alarm (network module doesn't export the
NAT id yet).

---

## 7. Incident response (plan 5.5)

**Severity matrix:**

| Sev | Definition | Examples | Response |
|---|---|---|---|
| **SEV1** | Core user flow down | login/checkout broken, API 5xx storm, DB down | drop everything; mitigate first, communicate |
| **SEV2** | Degraded, not down | AI eval slow/failing, one provider down | mitigate via flags; fix same day |
| **SEV3** | Cosmetic / minor | UI glitch, single non-critical endpoint | backlog |

**Loop:** (1) **Acknowledge** the alert. (2) **Localize** — CloudWatch + Sentry:
frontend? API? DB? Redis? AI provider? Follow the request by its trace id
(`TraceIDMiddleware`). (3) **Mitigate** — rollback (§8), scale (§11), or shed load
via a feature flag:
- `AI_EVAL_ENABLED=false` — stop LLM evaluation if the evaluator is failing/expensive.
- `RAG_PER_ACTIVITY_FEEDBACK=false` — disable per-activity RAG feedback.
- lower `AI_RATE_LIMIT_PER_MINUTE` — throttle AI load.

  Flags are task-def env, so changing one needs a redeploy — in a true emergency
  the **fastest lever is usually a rollback (§8)**, not a flag flip.

(4) **Communicate** status. (5) **Postmortem** — short writeup: what, when, root
cause, fix, prevention.

---

## 8. Deploy & rollback (plan 5.5 — operational; see also `DEPLOY.md`)

**Standard deploy:** merge to `main` triggers `deploy.yml` (or GitHub → *Actions →
deploy → Run workflow → production*): build **amd64** image → push `git-<sha>` to
ECR → run the **migration one-off task** (gated on exit 0) → ECS rolling update →
wait stable → smoke `/health/ready`. **Watch the run**; after green, confirm
`https://api.lingosai.com/health/ready` + a real login.

⚠️ **Never hand-build/push images** — Macs build arm64, which Fargate (amd64)
cannot pull (Phase 3 lesson). Always deploy through the pipeline.

**Rollback (backend)** — images are immutable by sha, so re-pointing the service
at the previous task-def revision is instant + safe:
```bash
# list revisions, newest last
aws ecs list-task-definitions --family-prefix lingosai-production-backend --region us-east-1
# re-point at the previous revision
aws ecs update-service --cluster lingosai-production --service lingosai-production-backend \
  --task-definition lingosai-production-backend:<previous-revision> --region us-east-1
aws ecs wait services-stable --cluster lingosai-production --services lingosai-production-backend \
  --region us-east-1
```

**Rollback (frontend)** — Vercel → *Deployments → previous → Promote to Production* (one click).

⚠️ The `lingos-ai-cli` user defaults to `ap-south-1`; **always pass `--region us-east-1`**.

---

## 9. Secret rotation (plan 5.5 — operational mechanics, extends §2)

```bash
# 1. write the new value
aws secretsmanager put-secret-value --secret-id lingosai/production/<NAME> \
  --secret-string "<new-value>" --region us-east-1
# 2. force tasks to pick it up (secrets are injected at task boot)
aws ecs update-service --cluster lingosai-production --service lingosai-production-backend \
  --force-new-deployment --region us-east-1
```
- **Provider keys** (OpenAI/Pinecone/Azure/Deepgram/Razorpay/Google): create new
  key in provider console → `put-secret-value` → `--force-new-deployment` →
  verify → **revoke the old key**.
- **`JWT_SECRET`** — rotating logs everyone out; do in a maintenance window.
- **`OTP_HASHING_SECRET`** — invalidates outstanding OTPs (low impact).
- **`DATABASE_URL` / `REDIS_URL`** — Terraform-owned; change via the data tier, not by hand.

---

## 10. Maintenance checklists (plan 5.6)

**Weekly:**
- [ ] Review Sentry top issues.
- [ ] Check the AI-cost trend (`ai_request_logs`) vs revenue.
- [ ] Confirm the latest RDS automated snapshot exists.
- [ ] Skim admin audit logs for anomalies.
- [ ] Merge Dependabot security PRs.
- [ ] Verify uptime-monitor history (once the synthetic check exists).

**Monthly (quarterly minimum for the drill):**
- [ ] Restore drill — verify a snapshot restores (§3).
- [ ] Review CloudWatch + AWS Budget spend; right-size RDS/Redis/tasks.
- [ ] Rotate any keys due on schedule (§9).
- [ ] Re-tighten AI rate limits from real `ai_request_logs` data.
- [ ] Apply RDS minor-version patches in a maintenance window.
- [ ] Review Trivy/CVE findings on the latest image.

---

## 11. Scaling triggers (plan 5.4 — quick reference)

| Stage | Users | Move |
|---|---|---|
| **1** | 0–500 | minimum footprint: 1 task (single worker until B4 is cross-process), `t4g` RDS Multi-AZ, `t4g` Redis, 1 NAT. Watch dashboards, don't add capacity. |
| **2** | 500–5k | finish B4 → multi-worker + ECS autoscaling (CPU/request target, 2–4 tasks); bump RDS class; consider a Celery worker for RAG notes. |
| **3** | 5k–20k | Savings Plans / Fargate Spot; CloudFront media caching; RDS Proxy / read replica; SQS for async work. |

Scale the **stateless tier (task count) first, the database last**.
