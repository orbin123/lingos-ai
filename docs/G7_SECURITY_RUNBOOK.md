# G7 — Security / hardening close-out (founder runbook)

Closes the final gap in `POLISHED_PRODUCTION_PLAN.md` §G7. Steps are tagged
**[AUTO]** (done in code this session) or **[FOUNDER]** (console / prod mutation).

---

## 1. HSTS on both hosts

**[AUTO]** Backend emits `Strict-Transport-Security: max-age=86400; includeSubDomains`
+ `X-Content-Type-Options: nosniff` on every production response
(`backend/app/core/security_headers.py`, wired in `main.py`; production-only).
Frontend (Vercel) sends the same via `frontend/next.config.ts` `headers()`.

> **Why short max-age + no preload:** the plan says "start with a short max-age."
> 1 day lets us back out fast if a sibling subdomain is found non-HTTPS. Once HSTS
> has been live and clean for a few weeks, bump to `max-age=31536000` and consider
> `preload` (submitting to the browser preload list is hard to reverse).

**[FOUNDER] verify after deploy** (both should show the header):
```bash
curl -sI https://api.lingosai.com/health        | grep -i strict-transport-security
curl -sI https://www.lingosai.com/              | grep -i strict-transport-security
# Expect: strict-transport-security: max-age=86400; includeSubDomains
```
Backend ships automatically on merge (CD); frontend ships on the Vercel deploy of
the same commit. No task-def or secret change is required for HSTS.

> When ready to harden, change `86400` → `31536000` in **both** files
> (`security_headers.py` `_HSTS_VALUE` and `next.config.ts`) in one PR.

---

## 2. config.py prod guard — re-confirmed [AUTO]

`app/core/config.py::_guard_production` already refuses to boot on every unsafe
prod combination (`DEBUG`, `SQL_ECHO`, `DEV_OTP_BYPASS`, empty `OTP_HASHING_SECRET`,
insecure cookie, localhost/empty CORS, missing S3 vars). Verified green this session
via `tests/unit/platform/test_config_prod_guard.py` (8 unsafe combos rejected, safe
config boots). No change needed — Appendix-C box "prod guard refuses unsafe boot" is
satisfied.

---

## 3. `backup*.sql` git-history decision

**Finding (read-only inspection this session):**
- `backup.sql` — **empty (0-byte)** blob in history. Harmless.
- `backup_pre_phase8.sql` (commit `ea59f01`, ~483 KB) — a real `pg_dump`. Contains
  **3 dev `users` rows** (two `@example.com` test accounts + the founder's own
  `@gmail.com`), their **bcrypt password hashes**, **2 `payments` rows** (provider
  IDs only — no raw card data, consistent with the "provider IDs only" design),
  **1 `oauth_accounts` row**. Dated May 2026, during the phase-8 build.
- Both files are **already absent from the current `main` tree** (deleted earlier);
  they live only in history.

**Classification:** **dev-stage data, NOT third-party production-user data** — public
signups are not open yet (reaching launch is the point of this plan). So this is not a
production-data exposure. However it does contain bcrypt hashes + the founder's real
email in history.

**Recommendation: purge as pre-launch hygiene (FOUNDER, optional-but-advised).**
It's the founder's own data and low-sensitivity, so this is *recommended*, not a
blocker. Purging requires a **destructive history rewrite on a protected branch**
(`enforce_admins: true`) — it invalidates all clones/open PRs — so it is a deliberate
founder action, not agent-run.

**[FOUNDER] purge procedure (if you choose to):**
```bash
# 0. Coordinate: no open PRs you care about; everyone re-clones afterward.
pip install git-filter-repo
git clone --mirror git@github.com:orbin123/lingos-ai.git lingos-mirror
cd lingos-mirror
git filter-repo --invert-paths --path backup.sql --path backup_pre_phase8.sql
# 1. Temporarily lift branch protection (it blocks force-push), then:
git push --force --mirror
# 2. Re-enable branch protection (see Session 2 in AGENT_PROGRESS for the exact rule).
# 3. Rotate the 3 dev-account passwords if any were reused anywhere real.
```
**If you'd rather not rewrite history:** that's defensible — the data is dev-only and
already removed from the tree. Just record the decision here. Either way, the box
"`backup*.sql` git-history decision made" is then ticked.

> Note: `.gitignore` should keep `backup*.sql` out going forward — confirm with
> `git check-ignore backup.sql` (add the pattern if it doesn't match).

---

## 4. Rotate provider keys to prod-dedicated values [FOUNDER]

Prod secrets were **seeded from the dev `.env`** (plan §G7). Rotate each provider key
to a fresh, prod-only value. **Leave `JWT_SECRET` and `OTP_HASHING_SECRET`** — those
were freshly generated for prod.

For each of `OPENAI_API_KEY`, `PINECONE_API_KEY`, `AZURE_SPEECH_KEY`,
`DEEPGRAM_API_KEY`, `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET`,
`RAZORPAY_WEBHOOK_SECRET`, `LANGCHAIN_API_KEY` (and `GOOGLE_CLIENT_SECRET` if it was
dev-shared):

1. Generate a new key in the provider console; revoke the old (dev-seeded) one.
2. Write it to Secrets Manager (the ARN is already wired in the task-def → no
   task-def revision needed):
   ```bash
   aws secretsmanager put-secret-value --region us-east-1 \
     --secret-id lingosai/production/OPENAI_API_KEY \
     --secret-string 'sk-…new…'
   ```
   (Secret-id format is `lingosai/production/<KEY>` — confirm the full list with
   `aws secretsmanager list-secrets --region us-east-1`.)
3. Roll the running tasks so they pick up the new values:
   ```bash
   aws ecs update-service --region us-east-1 \
     --cluster lingosai-production --service lingosai-production-backend \
     --force-new-deployment
   ```
4. After rollout: `scripts/verify-prod-parity.sh` → exit 0; smoke `api/health/ready`;
   for Razorpay, re-run a test purchase (G4 row) to confirm the new keys work.

> **Don't put new keys in any `.env` committed to the repo** — Secrets Manager is the
> source of truth in prod.

---

## Definition of done (Appendix-C boxes G7 closes)
- [ ] `DEBUG/SQL_ECHO/DEV_OTP_BYPASS=false`; prod guard refuses unsafe boot — **[AUTO] done** (test-proven; live values already false per G4 verifier).
- [ ] HSTS enabled on both hosts — **[AUTO] code shipped**; [FOUNDER] confirm the two `curl -sI` headers post-deploy.
- [ ] `backup*.sql` git-history decision made — **[FOUNDER]** record the decision above (purge or accept dev-only).
- [ ] Provider secrets rotated off dev-seeded values — **[FOUNDER]** §4.

When all four are ticked, **Appendix C is fully green → launch**.
