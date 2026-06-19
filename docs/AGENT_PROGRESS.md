# AGENT_PROGRESS

Execution log for closing `docs/POLISHED_PRODUCTION_PLAN.md`, one gap per session.
Most-recent session first.

---

## Session 6 — Gap G6: Observability finish (Sentry capture + trace correlation)

**Status:** **code complete; live proof is founder-gated.** The PR makes a forced
error reproducible and makes real prod 500s correlatable to CloudWatch by `trace_id`.
The actual close-out (populate the Sentry DSN value, set the Vercel DSN, confirm the
SNS subscription, deliver one alarm, observe the 503 path) is a founder runbook. G6 is
**not** marked done until those live proofs are captured.
**Branch:** `feat/g6-observability`
**Date:** 2026-06-19

### Why this gap
Phase A (G1–G3) is merged; G4/G5 are agent-complete + founder-gated. The plan's next
phase is **C = G6 + G8**, with G6 first, and Session 5 explicitly recommended G6 next.

### Critical finding (shaped the gap — most of G6 was already wired)
Exploration showed the heavy lifting already exists and needed **no change**:
backend + frontend Sentry init gated on the DSN (`app/core/sentry.py`, `main.py:48`);
`SENTRY_DSN` secret wired end-to-end (Secrets Manager → task-def → app); **11**
CloudWatch alarms + the `lingosai-production-alerts` SNS topic + email subscription
(`infra/terraform/modules/observability`); the `/health/ready` 503 path + ALB health
check. So G6 was **not** a build-from-scratch gap. The two real, agent-actionable holes:
1. **Real unhandled 500s were NOT correlatable to CloudWatch.** Only *manually-swallowed*
   exceptions got a `trace_id` tag (via `capture_to_sentry`); auto-captured unhandled
   exceptions — the actual prod bugs — reached Sentry with **no `trace_id`**.
2. **No deterministic way to force a verifiable error** in prod.

### Completed work (code)
- **`backend/app/core/sentry.py`** — `_before_send` now stamps the request-scoped
  `trace_id` onto `event["tags"]` (via `setdefault`, never overwriting an explicit tag).
  Runs at capture time inside the request contextvar scope, so it covers **both**
  auto-captured 500s and `capture_to_sentry` calls. No-op when no trace_id is bound.
- **`backend/app/modules/admin/routes.py`** — new `POST /admin/observability/test-error`,
  gated by `require_super_admin`. Logs `observability_test_error` with the `trace_id`,
  forwards a `RuntimeError` to Sentry via `capture_to_sentry` (tagged, no-op without DSN),
  and returns `JSONResponse(500, {status, detail, trace_id})`. Returns the id in the body
  so it can be matched in Sentry + CloudWatch; reports exactly once (no double-capture).
- **`backend/openapi.json`** — regenerated (`scripts/export_openapi.py`) for the new route,
  keeping the `openapi-drift` gate green.
- **No IaC change** — the alarms/SNS/secret wiring already existed.

### Files changed
- `backend/app/core/sentry.py`
- `backend/app/modules/admin/routes.py`
- `backend/openapi.json`
- `backend/tests/unit/platform/test_sentry.py` — 3 new `_before_send` trace_id tests.
- `backend/tests/integration/admin/test_observability_test_error.py` — new (500+trace_id
  for super-admin; 403 for admin-only).
- `docs/G6_OBSERVABILITY_RUNBOOK.md` — new (git-ignored dir → `git add -f`).
- `docs/AGENT_PROGRESS.md` — this log.

### Verification performed
- `uv run python -m pytest tests/unit/platform/ tests/integration/admin/` → **green**
  (14 targeted tests; full admin + platform suites pass). Note: per memory, used
  `uv run python -m pytest` (bare `uv run pytest` grabs a broken global pytest).
- `uv run ruff check` (4 changed files) → **All checks passed**;
  `uv run python -m mypy app/core/sentry.py app/modules/admin/routes.py` → **Success**.
- The integration test proves the route end-to-end via `TestClient` + `TraceIDMiddleware`:
  HTTP **500**, body `trace_id` is a 32-char hex, and the exception is forwarded to Sentry
  exactly once (stubbed for hermeticity).
- **Local-only artifact, not a regression:** my machine's repo-root `.env` carries a real
  `SENTRY_DSN`, so `app.main` (imported by the `tests.fixtures.client` plugin) initialises
  a live Sentry client and flushes a few events at exit. In CI there is no `.env`, so
  `settings.sentry_dsn` is empty and no client initialises — confirmed by re-running with
  `SENTRY_DSN=""`: 14 passed, **no Sentry flush**. My route test stubs `capture_to_sentry`,
  so it never sends regardless.

### Findings
- `before_send` is the single best correlation point: it fires for every event type and
  runs while the request contextvars are still bound — cleaner than fiddling with the
  Sentry scope stack inside middleware.
- Unlike G5 (which *added* a secret → needed a task-def revision), `SENTRY_DSN`'s ARN is
  **already referenced** in the live task-def. So the founder only needs to set the secret
  **value** and `--force-new-deployment`; **no task-def revision** is required.

### Decisions
- **No live mutation by the agent** — did not read/write the prod `SENTRY_DSN` value, set
  the Vercel var, confirm the SNS subscription, fire an alarm, or force a 503. All are
  prod-changing and/or console-only (founder runbook).
- **Forced-error route returns a handled 500** (not an unhandled raise) so it reports to
  Sentry exactly once and can still return the `trace_id` in the body. The `_before_send`
  tagging separately ensures *genuine* unhandled 500s are also correlatable.
- **Super-admin gating + single 500** keep the route safe in prod (well under the
  `alb_5xx` >10/60s threshold); not audited (it is not a mutation).
- Left the route in prod as a permanent self-test (documented as removable).

### Risks
- The PR proves the *mechanism* (capture + tagging + a forced 500), not that prod is
  actually capturing — that needs the **real DSN value** in Secrets Manager + Vercel. Until
  the founder sets those, Sentry capture in prod stays a no-op. Made explicit in the runbook
  + its "definition of done".
- The faithful 503 test briefly removes the only healthy ECS target (single task) — the
  runbook flags doing it in a quiet window and offers a safe `set-alarm-state` alternative.
- `TF_VAR_alert_email` must be passed on **every** `terraform apply` or the SNS subscription
  is destroyed (pre-existing gotcha; re-stated in the runbook + `docs/AWS_SETUP.md`).

### Founder actions required (to finish G6 — see `docs/G6_OBSERVABILITY_RUNBOOK.md`)
1. **Review + merge** PR `feat/g6-observability`.
2. Ensure `SENTRY_DSN` (Secrets Manager) holds a real value; `--force-new-deployment`.
3. Set `NEXT_PUBLIC_SENTRY_DSN` in Vercel; redeploy the frontend.
4. `POST /admin/observability/test-error` with a super-admin token → confirm the returned
   `trace_id` in Sentry **and** CloudWatch.
5. Confirm the SNS email subscription; fire one alarm (`set-alarm-state`) → confirm delivery.
6. Observe the `/health/ready` 503 path (safe `set-alarm-state` or the faithful RDS-block).

### Next recommended gap
**G8 — rollback drill + DR** (Phase C's other half): largely founder-driven (time a real
rollback <5 min; row-verify an RDS restore), but the agent can pre-write the drill runbook
+ any helper scripts. Alternatively **G7 — security close-out** (Phase D): the agent can do
the `config.py` prod-guard re-confirmation, the HSTS header change, and the `backup*.sql`
git-history decision in code, leaving key rotation as founder console work.

---

## Session 5 — Gap G5: Email provider (SES → Resend)

**Status:** **code/IaC complete; live flip is founder-gated.** The PR makes Resend the
desired-state prod email provider and wires the `RESEND_API_KEY` secret + execution-role
grant; the actual live cutover (domain verify, key, task-def revision, external-inbox
test) is a founder runbook. G5 is **not** marked done until an email reaches an external
inbox.
**Branch:** `feat/g5-email-resend`
**Date:** 2026-06-19

### Why this gap
Phase A (G1–G3) is merged; G4 is agent-complete (verifier + runbook) with only
founder browser/purchase rows left. Session 4 recommended **G5 next** because it
**directly unblocks G4 row 6** (signup OTP email) and finishes Phase B.

### Decision gate — verified live (read-only)
SES production access is **DENIED / sandbox-only** — confirmed this session:
```
aws sesv2 get-account → "ProductionAccessEnabled": false,
  "ReviewDetails": {"Status":"DENIED","CaseId":"178170275200223"}
```
Sandbox can only email verified identities, never an arbitrary inbox. Per the plan's
decision gate (and founder approval this session), prod sends via **Resend**.

### Critical architectural finding (shaped the whole gap)
`deploy.yml` builds each new task-def by **cloning the currently-running task-def**
(`describe-task-definition`) and swapping only the image; the compute module has
`lifecycle { ignore_changes = [container_definitions] }`. So **neither `terraform apply`
nor a normal code deploy changes the live `environment`/`secrets`** — the live flip is a
**one-time founder task-def revision** (after which deploy.yml carries it forward). There
is also a load-bearing ordering: the execution role only reads ARNs in `all_secret_arns`,
so `terraform apply` (creates the secret + widens the grant) **must precede** the task-def
revision that references `RESEND_API_KEY`. Both captured in the runbook.

### Completed work (code/IaC)
- **`infra/terraform/modules/stack/main.tf`** — `EMAIL_PROVIDER` `"ses"` → `"resend"`
  (left `SES_REGION`/`EMAIL_FROM` for an easy switch-back; `EMAIL_FROM` already on the
  `lingosai.com` domain).
- **`infra/terraform/modules/secrets/main.tf`** — added `RESEND_API_KEY` to
  `founder_secret_names`, which (a) creates the empty Secrets Manager entry, (b) adds it to
  the task-def `secrets` wiring (`secret_arns`), and (c) widens the execution-role
  `GetSecretValue` grant (`all_secret_arns`).
- **`scripts/verify-prod-parity.sh`** — now asserts `EMAIL_PROVIDER=resend` (was
  "non-empty") and adds `RESEND_API_KEY` to `EXPECTED_SECRETS`, so G5 + G4-row-6 are
  CLI-verifiable post-flip.
- **`docs/G5_EMAIL_RUNBOOK.md`** (new) — exact founder steps: Resend domain verify +
  DKIM/SPF, create key, `terraform apply`, `put-secret-value`, the one-time task-def
  revision (copy-paste `aws ecs` block), external-inbox proof, verifier re-run, rollback.
- **No app code change** — `app/email/` already supports `EMAIL_PROVIDER=resend` +
  `RESEND_API_KEY` with a console fallback (confirmed in `app/email/__init__.py`).

### Files changed
- `infra/terraform/modules/stack/main.tf`
- `infra/terraform/modules/secrets/main.tf`
- `scripts/verify-prod-parity.sh`
- `docs/G5_EMAIL_RUNBOOK.md` — new (git-ignored dir → `git add -f`).
- `docs/AGENT_PROGRESS.md` — this log.

### Verification performed
- `terraform fmt -check` on both modules → clean (exit 0).
- `terraform validate` (stack module, `-backend=false`) → **Success** (the lone warning is
  a pre-existing `data.aws_region.current.name` deprecation in `compute/main.tf`, unrelated).
- `bash -n scripts/verify-prod-parity.sh` → OK.
- **Ran the verifier against LIVE prod** — the new assertions correctly report the
  **pre-flip** state: `EMAIL_PROVIDER` FAIL (`got 'ses'`), `secret wiring` FAIL
  (`missing: RESEND_API_KEY`), `PASS=12 FAIL=2 WARN=1`. These two flip to PASS once the
  founder completes the runbook — proving the logic and giving a clear "not done yet" signal.

### Findings
- `RESEND_API_KEY` did **not** exist in Secrets Manager (prod list confirmed) — so before
  this PR, Resend was unusable in prod even with the code support: no secret, no task-def
  wiring, no IAM grant.
- The live `EMAIL_PROVIDER` is still `ses` and won't change from IaC alone (ignore_changes
  + deploy.yml inherits live env) — the one-time task-def revision is unavoidable.

### Decisions
- **Resend over re-appealing SES** (founder-approved) — SES re-review is console-only,
  slow, and uncertain; Resend unblocks launch now.
- **No live mutation by the agent** — did not `terraform apply`, register a task-def, write
  the secret, or send a test email. All depend on the real Resend key + domain verification
  (founder-only) and are prod-changing.
- Kept `SES_REGION`/SES IAM (`ses:SendEmail` on the task role) in place — harmless, and
  makes a switch-back trivial if SES prod access is later granted.

### Risks
- The PR changes **desired state** only; until the founder runs the runbook, live prod
  still emails via sandboxed SES (external inboxes won't receive). The verifier's two FAILs
  make this visible.
- Resend needs its **own** DKIM/SPF records at Namecheap (separate from SES's). If only SES
  records exist, Resend delivery will fail SPF/DKIM alignment → spam/bounce. Called out in
  runbook Step 1.
- `EMAIL_FROM=noreply@lingosai.com` requires the domain **verified in Resend**; until then
  Resend only sends from `onboarding@resend.dev` to the account owner. Runbook Step 1.

### Founder actions required (to finish G5 — see `docs/G5_EMAIL_RUNBOOK.md`)
1. **Review + merge** PR `feat/g5-email-resend`.
2. Verify `lingosai.com` in Resend + publish its DKIM/SPF at Namecheap.
3. Create a Resend API key.
4. `terraform apply` in `envs/production` (creates the secret + IAM grant).
5. `aws secretsmanager put-secret-value` the real key.
6. Run the one-time task-def revision (runbook Step 5) to flip live `EMAIL_PROVIDER=resend`
   + reference the secret; wait stable.
7. Sign up on `www` with an **external** inbox; confirm the OTP arrives (G5 + G4 row 6
   evidence). Re-run `scripts/verify-prod-parity.sh` → both checks PASS.

### Next recommended gap
Phase B closes once the founder finishes the G5 runbook + the remaining G4 founder rows.
The next agent-actionable gap is **G6 — observability finish**: the agent can pre-wire
`SENTRY_DSN` consumption / a forced-error test route and document the SNS-subscription +
503-resilience checks, leaving the DSN value + subscription click as founder actions.
(Note: `SENTRY_DSN` already exists as a secret; confirm it holds a real value.)

---

## Session 4 — Gap G4: Prove feature parity in prod (verifier + runbook)

**Status:** **partially complete** — the CLI-checkable rows are **proven live**
(verifier exits 0); the browser/purchase rows remain **founder actions** with an
exact runbook. G4 is *not* marked done (it can't be, without human live proof).
**Branch:** `feat/g4-prod-parity-verify`
**Date:** 2026-06-19

### Why this gap
Phase A (G1+G2+G3) is fully merged (`#101`–`#105`); `main` is protected and
auto-deploys with smoke+rollback. The plan's next phase is **B = G4 + G5**, and
G4 is listed first. (Note: Session 3's "PR not merged" status below is stale —
G3 merged as `#104`/`#105`, confirmed in git log.)

### Honest scope (per charter)
G4's close-condition is *"every row has a screenshot/log/CLI proof."* ~half the
13-row matrix is **CLI-provable by the agent** (health, www, ECS, env/secret
wiring, media S3/CDN infra); the other half needs a **human browser or a live
purchase** (OAuth, Razorpay, WebSocket session, pronunciation, Deepgram, RAG).
The agent **automated + proved the former** and **wrote an exact founder
runbook** for the latter. G4 stays **partial** until the founder rows are ticked.

### Completed work (code)
- **`scripts/verify-prod-parity.sh`** — new **read-only** verifier (curl GET/HEAD
  + `aws describe/list` only; no mutations). Prod defaults, overridable via env
  (`API_URL`, `WWW_URL`, `ECS_*`, `AWS_REGION`). Tiny PASS/FAIL/WARN framework;
  exits non-zero on any FAIL. Checks: api `/health` + `/health/ready`
  (DB+Redis), `www` 200, ECS service running==desired & ACTIVE, task-def env
  (`STORAGE_BACKEND=s3`, `EMAIL_PROVIDER`, `MEDIA_S3_BUCKET`, `MEDIA_CDN_URL`,
  `DEBUG=false`, `DEV_OTP_BYPASS=false`), 13 feature secrets wired (names only,
  values never read), both media buckets exist, CloudFront reachable, and a
  media write→serve probe (WARN when the bucket is empty awaiting app traffic).
- **`docs/PROD_PARITY_RUNBOOK.md`** — the 13-row matrix, each row tagged
  **[AUTO]** or **[FOUNDER]** with click-paths + the evidence to capture; records
  this session's live run and a clear "definition of done for G4."

### Files changed
- `scripts/verify-prod-parity.sh` — new verifier.
- `docs/PROD_PARITY_RUNBOOK.md` — new runbook (git-ignored dir → `git add -f`).
- `docs/AGENT_PROGRESS.md` — this log.

### Commits
- `feat(scripts): add read-only prod feature-parity verifier (G4)`
- `docs(g4): add prod feature-parity runbook (AUTO + FOUNDER rows)`
- (this doc commit)

### Verification performed (live, this session)
- `bash -n scripts/verify-prod-parity.sh` → OK (shellcheck not installed locally).
- **Ran the verifier against LIVE prod** (account `924903313980`, us-east-1):
  **`PASS=14 FAIL=0 WARN=1`, exit 0.** Proven green: `api/health` 200,
  `api/health/ready` 200 `{database:ok,redis:ok}`, `www` 200, ECS
  `1/1 ACTIVE (lingosai-production-backend:7)`, `STORAGE_BACKEND=s3`,
  `EMAIL_PROVIDER=ses`, `MEDIA_S3_BUCKET=lingosai-production-media`,
  `MEDIA_CDN_URL=https://d3ekrhb69b5j9n.cloudfront.net`, both media buckets
  exist, CloudFront reachable (403 on root = no object, domain live), all 13
  secrets wired, `DEBUG=false`, `DEV_OTP_BYPASS=false`.
- **WARN explained:** `s3://lingosai-production-media` has **0 objects** — no
  TTS/image has been generated in prod yet. Infra is proven; the write→serve
  proof needs one real session (runbook row 5).

### Findings
- Live prod config is correct and matches Appendix A: `STORAGE_BACKEND=s3`,
  `DEBUG/SQL_ECHO/DEV_OTP_BYPASS=false`, all 15 secrets referenced (13 feature +
  `JWT_SECRET`/`OTP_HASHING_SECRET`). No local-only misconfiguration found in the
  env-driven layer — nothing to "fix that only worked locally" at this level.
- `EMAIL_PROVIDER=ses` is still the live value → row-6 OTP email to an external
  inbox will likely fail until **G5** flips it to Resend (SES prod access denied).
  This is a known G5 dependency, not a row-6 bug; noted in the runbook.

### Decisions
- **Read-only by design** — the verifier never mutates prod (no test signups, no
  purchases, no media writes). The mutation-driven proofs are founder rows.
- Media write→serve is a **WARN, not FAIL**, when the bucket is empty — an empty
  bucket pre-traffic is expected, not a regression.
- Did **not** attempt browser automation / live Razorpay — explicitly out of
  scope (founder-only), per the plan and charter.
- Secret **wiring** asserted from the task-def (names), not Secrets Manager
  values — proves parity without `GetSecretValue` and without reading secrets.

### Risks
- The verifier proves **wiring + reachability**, not end-to-end *behaviour* for
  the AI features. A capability can be wired yet fail at runtime (e.g. an expired
  provider key) — only the [FOUNDER] rows catch that. This is inherent to G4 and
  why those rows can't be agent-closed.
- `MEDIA_CDN_URL` root returns 403 (no default-root-object) — benign, but if a
  real object later 403s via the CDN, that's a CloudFront OAC/bucket-policy bug to
  file (called out in runbook row 5).

### Founder actions required (to finish G4)
1. **Review + merge** PR `feat/g4-prod-parity-verify`.
2. Work the **[FOUNDER] rows 5–13** in `docs/PROD_PARITY_RUNBOOK.md` on the prod
   hostnames, attaching the stated evidence. Re-run `scripts/verify-prod-parity.sh`
   after a real session to flip **media write→serve** to PASS (row 5).
3. **Likely blocker:** row 6 (OTP email) probably needs **G5** first — flip
   `EMAIL_PROVIDER` ses→resend (SES prod access denied). Decide G5 at/with G4.

### Next recommended gap
**G5 — email provider** (small, mostly founder/console): if SES is still
sandboxed, set the prod task-def `EMAIL_PROVIDER=resend`, ensure `RESEND_API_KEY`
is in Secrets Manager + the Resend domain is verified, redeploy, and send a real
email to an external inbox. It directly unblocks G4 row 6 and finishes Phase B.

---

## Session 3 — Gap G3: Post-deploy live smoke (api + www)

**Status:** code implemented; PR open, **not merged**. The smoke step only *executes* on a real
deploy (`push: main`), so live-pipeline proof is the next merge — but the assertion logic is proven
green against live prod here (see Verification).
**Branch:** `feat/g3-postdeploy-smoke`
**Date:** 2026-06-18

### Why this gap
Completes the Phase A CI/CD-lockstep trio (G1 auto-deploy + G2 branch protection + **G3 smoke**).
Appendix C requires the post-deploy smoke to cover **both** api + www; today `deploy.yml` only
smoke-tests api `/health/ready`.

### Completed work (code)
- **Extended `deploy.yml`** with a final `Post-deploy smoke (frontend www)` step: curls
  `https://www.lingosai.com` (overridable via `vars.FRONTEND_SMOKE_URL`), retries 10×/6s, and **fails
  the run** if it never returns 200.
- **Backend rollback semantics preserved:** the existing `/health/ready` smoke remains the *only*
  step that triggers ECS rollback. The new www step does **NOT** roll back the backend — the frontend
  is an independent Vercel deploy (AD-1), so a down www is not a backend regression. This matches the
  plan's "fail the run if either host is down" without rolling back a healthy backend.
- Updated the workflow header comment to document the two-stage smoke.
- Removed the stray empty `frontend/e2e/` directory.

### Findings (phantom-E2E cleanup — mostly already done in the repo)
The plan's G3 also says "delete every reference to the non-existent Playwright suite / `e2e-up.sh` /
`e2e.yml`." Investigation shows the **active repo already carries none of these**:
- No `e2e.yml`, no `scripts/e2e-up.sh`/`e2e-down.sh`, no `playwright.config.*`.
- `frontend/e2e/` was an **untracked empty dir** (git ignores empty dirs → nothing was ever in
  version control); removed locally for tidiness.
- The only remaining `playwright` token is a **transitive peer/optional-dep declaration in
  `frontend/package-lock.json`** (`@playwright/test` under another package), **not** an installed
  suite. Left untouched — editing the lockfile by hand is risky and out of G3 scope.
- The narrative phantom-E2E claims live only in the historical build-log docs
  (`PRODUCTION_COMPLETION_PLAN.md`, `complete_production_plan.md`), which POLISHED explicitly keeps as
  history. No active artifact remains to strip.

### Files changed
- `.github/workflows/deploy.yml` — add frontend www smoke step + header comment.
- `frontend/e2e/` — removed (was empty/untracked).
- `docs/AGENT_PROGRESS.md` — this log.

### Verification performed
- **YAML valid:** `ruby -ryaml -e "YAML.load_file('.github/workflows/deploy.yml')"` → OK.
- **Assertion logic proven against LIVE prod** (the exact curl the step runs):
  `curl -fsSL .../www.lingosai.com` → **200**; `curl -fsS .../api/health/ready` → **200**.
- **Live-pipeline proof is intentionally NOT here** — `deploy.yml` runs only on `push: main`, not on
  a PR branch, so the smoke step first *executes in the pipeline* on the next deploy (founder observes
  it on the merge run, same pattern as G1).

### Decisions
- www smoke **does not** trigger backend rollback (independent Vercel system).
- Did **not** add an authenticated critical-path GET — that needs a CI test-user secret and belongs to
  the post-launch Playwright critical-path (§6). The api `/health/ready` smoke already exercises a real
  app path (DB + Redis), satisfying "a cheap app GET."
- Did **not** edit `package-lock.json` (transitive reference only).

### Risks
- The www smoke runs **after** a successful backend deploy + rollback gate. If www is down, the job
  goes red but the (healthy) backend stays deployed — intended, but means a red deploy run can
  coexist with a healthy api. Documented in the step's error message.
- `FRONTEND_SMOKE_URL` is unset in the GitHub Environments, so the hardcoded default
  `https://www.lingosai.com` is used. Fine for production; a staging dispatch would smoke the prod
  www unless the var is set (noted for whoever wires staging).

### Founder actions required
1. **Review + merge** PR `feat/g3-postdeploy-smoke`.
2. On the next deploy (the merge run, or a `workflow_dispatch`), **observe** the new
   `Post-deploy smoke (frontend www)` step run green after the api smoke.

### Next recommended gap
Phase A (G1+G2+G3) is now code-complete. Next is **Phase B — prove feature parity in prod (G4)**:
walk the G4 matrix end-to-end on `www.lingosai.com` and resolve the email provider (G5). Most of G4
is founder-driven live verification (browser OAuth loop, real TTS→S3 write, Razorpay test purchase),
so the agent's role there is mainly fixing anything that only worked locally + scripting CLI proofs
(e.g. confirming an S3 object lands in `MEDIA_S3_BUCKET`).

---

## Session 2 — Gap G2: Branch protection on `main`

**Status:** ✅ **COMPLETE.** Path-filter fix merged ([#102](https://github.com/orbin123/lingos-ai/pull/102),
merge `360aee4`); branch protection enabled post-merge via `gh api` and verified live.
**Branch:** `feat/g2-branch-protection` (fix) + `docs/g2-protection-enabled` (this completion note).
**Date:** 2026-06-18

### Why this gap, why now
G1 merged (`43ee238`), so `push: main` now auto-deploys the backend **with no gate**. Until G2
lands, every merge to `main` is an unattended prod deploy with no required-check guard rail. G2 is
the guard rail. Verified pre-state: `gh api .../branches/main/protection` → **404 "Branch not
protected."**

### The Appendix B path-filter gotcha (handled first, as the plan requires)
Every CI workflow's `pull_request` trigger was `paths:`-filtered. If those jobs are marked
**required** under `strict: true`, a PR that doesn't touch the filtered path never triggers the job,
so the required context never reports and the PR can **never merge**. Fix: drop the `paths:` filter
from the `pull_request` trigger in the four workflows whose jobs become required contexts, so every
PR runs every required gate.

### Completed work (code)
- Removed the `paths:` block from the **`pull_request`** trigger of `backend.yml`, `frontend.yml`,
  `contract.yml`, `docker.yml` (added an explanatory comment in each). Every PR now runs:
  `lint`, `types`, `unit`, `integration`, `migrations`, `coverage` (backend), `ci` (frontend),
  `openapi-drift` (contract), `docker-build` (docker).
- **Left `push:` paths filters intact** — post-merge `push: main` runs don't gate PRs, so there's no
  reason to burn CI minutes there.
- **Left `backend-curriculum.yml` untouched** — `curriculum-seed-smoke` stays optional per the plan
  (Appendix B lists it "optional to require"), so its path filter can stay.

### Branch-protection enablement — ✅ DONE post-merge (verified live)
Decisions captured + applied: `required_approving_review_count: 0` (solo-founder self-merge),
`strict: true`, `enforce_admins: true`, 9 required contexts (curriculum-seed-smoke NOT required).
After #102 merged, the agent ran the PUT below (via JSON `--input` for a clean `restrictions: null`).
**Read-back proof** (`gh api .../branches/main/protection`):
`{strict:true, contexts:[lint,types,unit,integration,migrations,coverage,ci,openapi-drift,docker-build],
enforce_admins:true, required_reviews:0, restrictions:null}`.
```bash
gh api -X PUT repos/orbin123/lingos-ai/branches/main/protection \
  -F 'required_status_checks.strict=true' \
  -F 'required_status_checks.contexts[]=lint' \
  -F 'required_status_checks.contexts[]=types' \
  -F 'required_status_checks.contexts[]=unit' \
  -F 'required_status_checks.contexts[]=integration' \
  -F 'required_status_checks.contexts[]=migrations' \
  -F 'required_status_checks.contexts[]=coverage' \
  -F 'required_status_checks.contexts[]=ci' \
  -F 'required_status_checks.contexts[]=openapi-drift' \
  -F 'required_status_checks.contexts[]=docker-build' \
  -F 'required_pull_request_reviews.required_approving_review_count=0' \
  -F 'enforce_admins=true' -F 'restrictions='
```
(Includes `migrations`, which `DEPLOY.md` §5 omits.)

### Files changed
- `.github/workflows/backend.yml` — drop PR-trigger `paths:`.
- `.github/workflows/frontend.yml` — drop PR-trigger `paths:`.
- `.github/workflows/contract.yml` — drop PR-trigger `paths:`.
- `.github/workflows/docker.yml` — drop PR-trigger `paths:`.
- `docs/AGENT_PROGRESS.md` — this log.

### Verification performed
- **YAML valid:** `ruby -ryaml -e "YAML.load_file(...)"` on all four → OK.
- **Trigger structure confirmed:** parsed each `on:` — `pull_request.paths` is now **(none)** on all
  four; `push.branches=[main]` and `push.paths` still present (intentional).
- **Context names verified against job names** in the workflow files: backend jobs `lint/types/unit/
  integration/migrations/coverage`, frontend `ci`, contract `openapi-drift`, docker `docker-build` —
  all 9 match the plan's required list exactly.
- **This PR self-proves the gates:** it edits all four `.github/workflows/*.yml` files, which match
  each workflow's own `.github/workflows/*.yml` path filter, so every required check runs on this PR.
- **All 9 required contexts passed green on #102 itself** (live self-proof the de-filtered triggers
  fire), plus DCO + Vercel. Merge `360aee4`.
- **Branch protection verified live** post-merge — read-back matches the intended rule (above).

### Decisions
- Drop `paths:` only on the **PR** trigger (Appendix B "Recommended" option), not the push trigger.
- Keep `curriculum-seed-smoke` optional → its workflow is untouched.
- Self-merge (`review_count: 0`) + `enforce_admins: true` (founder decisions, captured above).

### Risks
- ⚠️ **Ordering is load-bearing:** branch protection must be enabled **only after** this PR merges.
  Enabling it while this PR is open would immediately require the (now-unfiltered) contexts on it —
  which is fine for *this* PR (it triggers them all) but would wedge any *other* open PR that hasn't
  re-run since the filter change. Enable post-merge.
- After enablement with `enforce_admins: true`, the founder can no longer push directly to `main` —
  all changes go through PRs. This is intended.
- More CI minutes: every PR (incl. dependabot, docs-only) now runs the full backend+frontend+docker+
  contract suite. Acceptable at this repo size (the plan's stated trade-off).

### Founder actions required
- None outstanding for G2. (#102 merged; protection enabled + verified by the agent.)
- ⚠️ **New reality:** `main` is now protected with `enforce_admins: true` — *all* changes (incl.
  docs) must go through a PR; direct pushes to `main` are rejected for everyone.
- (Optional) Confirm the guard rail yourself by opening a throwaway PR with a deliberately failing
  check and verifying it cannot be merged.

### Next recommended gap
**G3 — post-deploy live smoke** (extend the `deploy.yml` `/health/ready` smoke to also assert
`https://www.lingosai.com` 200 + one cheap authenticated GET) and **delete the stray empty
`frontend/e2e/` directory** + any remaining phantom-E2E references. Small, no live-prod risk, and it
completes the Phase A "CI/CD lockstep" trio (G1+G2+G3).

---

## Session 1 — Gap G1: CI/CD lockstep (auto-deploy + auto-rollback)

**Status:** implemented; PR open, **not merged** (merge = first live auto-deploy — founder-gated).
**Branch:** `feat/g1-cicd-lockstep`
**Date:** 2026-06-18

### Completed work
- **G1.1** — `deploy.yml` now triggers on `push: branches: [main]` (alongside `workflow_dispatch`).
- **G1.2** — Fixed the env/concurrency binding: both `environment:` and `concurrency.group` now
  resolve `${{ github.event.inputs.environment || 'production' }}` (was bare `inputs.environment`,
  which is **null on a push** → would fail to target the `production` GitHub Environment / OIDC role).
- **G1.3** — Added a "Capture current task-def (rollback target)" step before the rolling update;
  rewrote the smoke step to, on failure, re-point the service at that task-def, wait for stable, and
  fail the job (was a manual "roll back yourself" message).
- **G1.4** — Removed the dead `DATE_TAG` from the "Compute image tags" step (immutable ECR repo only
  ever pushes `git-<sha>`).
- **G1.5** — Doc-only: documented in `DEPLOY.md` §4 that a `main` merge fires Vercel (FE) + `deploy.yml`
  (BE) on the same commit. No code; live confirmation is a founder observation.
- Reconciled `DEPLOY.md` §2/§4/§6 with the implemented workflow (single immutable tag; auto-rollback;
  forward-only migration caveat; automatic push trigger).

### Files changed
- `.github/workflows/deploy.yml` — trigger, env binding, rollback, date_tag removal.
- `docs/DEPLOY.md` — §2 tag scheme, §4 lockstep note, §6 implemented-behavior rewrite.
- `docs/AGENT_PROGRESS.md` — this log.

### Commits
- `1a49bef ci(deploy): auto-deploy on push to main, fix env binding, add auto-rollback`
- `1646ad9 docs(deploy): reconcile DEPLOY.md with the implemented deploy.yml`
- (this doc commit)

### Verification performed
- **YAML valid:** `ruby -ryaml -e "YAML.load_file('.github/workflows/deploy.yml')"` → OK
  (also via backend venv `python -c "import yaml; yaml.safe_load(...)"` → OK).
- **Env binding target exists:** `gh api repos/orbin123/lingos-ai/environments` lists `production`;
  `.../environments/production/variables` carries all 10 vars the workflow reads
  (AWS_DEPLOY_ROLE_ARN, AWS_REGION, ECR_REPOSITORY, ECS_CLUSTER, ECS_MIGRATE_FAMILY,
  ECS_SECURITY_GROUP, ECS_SERVICE, ECS_SUBNETS, ECS_TASK_FAMILY, HEALTHCHECK_URL). So on a push the
  job binds to `production` and the OIDC role + vars resolve.
- **Diff review:** `date_tag` fully removed; both env references use `|| 'production'`; rollback step
  references `$PREV_TD` captured before the rolling update.
- **Live deploy/rollback proof is intentionally NOT done here** — it deploys to real prod and is a
  founder action (see below).

### Findings
- The phantom-E2E references the plan's G3 mentions live **only** in the historical docs
  (`PRODUCTION_COMPLETION_PLAN.md`, `complete_production_plan.md`), which POLISHED explicitly keeps as
  build logs. The active workflows had **no** e2e references. Only stray active artifact is the empty
  `frontend/e2e/` directory (left for G3).
- There is **no lowercase `staging` GitHub Environment** (only `production`). The `workflow_dispatch`
  default is `staging`, so a manual staging dispatch would fail to bind an environment. Pre-existing,
  out of G1 scope — noted for whoever wires staging.

### Decisions
- Kept the smoke gate on `/health/ready` only (did **not** extend to `www` / a public GET) — that is
  G3's scope, deliberately deferred to keep this one gap.
- Auto-rollback is **service-only** (re-point task-def). Migrations are forward-only and are **not**
  reverted — documented in both the workflow and `DEPLOY.md`.

### Risks
- ⚠️ **No branch protection yet (G2).** With `push: main` live, *every* merge to `main` triggers an
  immediate **production** deploy with **no required-status-check gate**. Until G2 lands, merge to
  `main` deliberately. **This makes G2 the necessary next gap.**
- First merge after this PR = the first unattended prod deploy. Recommend the founder run the manual
  `workflow_dispatch → production` check first (below) to prove the binding before relying on push.

### Founder actions required (live proof — cannot be done by the agent)
1. **Review + merge** PR `feat/g1-cicd-lockstep`. Merging is the first live auto-deploy — be ready.
2. **(Recommended first) Manual binding check:** Actions → `deploy` → "Run workflow" →
   `environment: production`. Confirm it assumes the OIDC role, builds/pushes `git-<sha>`, migration
   exits 0, ECS rollout `COMPLETED`, smoke 200. This proves G1.2 without depending on a merge.
3. **Auto-deploy proof:** after merge, watch Actions auto-run `deploy` on the merge commit → new ECR
   `git-<sha>` → migrate exit 0 → rollout COMPLETED → smoke 200; confirm Vercel deployed the same
   commit (G1.5).
4. **(Optional) Rollback proof:** in a dispatch run, point `HEALTHCHECK_URL` at a failing URL (or
   otherwise force smoke red) and confirm the service is re-pointed at the prior task-def and the job
   fails.

### Next recommended gap
**G2 — branch protection on `main`** (Appendix B): first resolve the path-filter gotcha (drop
`paths:` filters or add always-pass dummy jobs), then enable required contexts incl. `migrations`.
It is the guard rail this gap's auto-deploy requires.
