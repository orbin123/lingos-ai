# Production Feature-Parity Runbook (G4)

> **Purpose:** prove that **every** capability that works locally also works on
> live prod (`www.lingosai.com` / `api.lingosai.com`) — principle #1 of
> [`POLISHED_PRODUCTION_PLAN.md`](./POLISHED_PRODUCTION_PLAN.md) §G4.
>
> Each row below is tagged **[AUTO]** (proven by `scripts/verify-prod-parity.sh`)
> or **[FOUNDER]** (needs a human browser, a live purchase, or a real session —
> cannot be done from a shell). Tick a box only with the stated **evidence**
> attached (a screenshot, a log line, or CLI output).
>
> ⚠️ `docs/` is git-ignored — force-add this file: `git add -f docs/PROD_PARITY_RUNBOOK.md`.

---

## How to run the [AUTO] checks

```bash
# From the repo root, with AWS CLI authenticated for the prod account
# (the read-only lingos-ai-cli user is enough):
./scripts/verify-prod-parity.sh | tee /tmp/parity-$(date +%Y%m%d).log
```

The script is **read-only** (only `curl` GET/HEAD and `aws describe/list`). It
exits `0` when every [AUTO] check passes; an empty media bucket is a `WARN`, not
a failure (it just means no TTS/image has been generated in prod **yet** — see
row 5).

**Last automated run — 2026-06-19 (this session):** `PASS=14 FAIL=0 WARN=1`
(WARN = media bucket empty, awaiting first live TTS/image). Verified live:
`api/health` 200, `api/health/ready` 200 `{database:ok, redis:ok}`, `www` 200,
ECS `1/1 ACTIVE` (`lingosai-production-backend:7`), `STORAGE_BACKEND=s3`,
`EMAIL_PROVIDER=ses`, both media buckets exist, CloudFront reachable, all 13
feature secrets wired, `DEBUG=false`, `DEV_OTP_BYPASS=false`.

---

## The G4 matrix — 13 rows

| # | Capability | Tag | Status | Evidence to capture |
|---|---|---|---|---|
| 1 | API health (DB+Redis) | [AUTO] | ✅ proven | `/health/ready` 200 `{database:ok,redis:ok}` |
| 2 | Frontend served | [AUTO] | ✅ proven | `www` 200 |
| 3 | Backend running zero-downtime | [AUTO] | ✅ proven | ECS `1/1 ACTIVE` |
| 4 | Env + secret wiring | [AUTO] | ✅ proven | task-def env/secrets asserted |
| 5 | TTS / imagegen / STT → S3 → CDN | [AUTO]+[FOUNDER] | 🟡 infra proven, write pending | object lands in bucket + serves via CDN |
| 6 | Auth signup + OTP email | [FOUNDER] | ⬜ | OTP arrives at an external inbox |
| 7 | Google OAuth loop | [FOUNDER] | ⬜ | consent → logged in; cookie survives refresh |
| 8 | Learning-session WebSocket | [FOUNDER] | ⬜ | live `learning_session.event.v1` events |
| 9 | Scoring engine | [FOUNDER] | ⬜ | scorecard + SkillPoints update after an activity |
| 10 | Pronunciation (Azure) | [FOUNDER] | ⬜ | a pronunciation score returns |
| 11 | Deepgram streaming STT | [FOUNDER] | ⬜ | A2Z speaking widget transcribes |
| 12 | RAG feedback memory (Pinecone) | [FOUNDER] | ⬜ | repeat-weakness feedback cites a prior session |
| 13 | Razorpay billing + Admin/audit + AI-cost | [FOUNDER] | ⬜ | test purchase grants entitlement; mutation in audit log |

> Rows 1–4 are closed by the script. Row 5's **infrastructure** is proven; the
> **write→serve** half needs one real session (below). Rows 6–13 are the
> founder click-throughs below.

---

## [FOUNDER] step-by-step

> Do these on the **prod hostnames** in a normal browser (not localhost). Where
> a step says "re-run the verifier", that's `scripts/verify-prod-parity.sh`.

### Row 5 — Media write→serve (finish the [AUTO] WARN)
1. Log into `www.lingosai.com` and start any lesson that plays audio (teacher
   TTS) or shows a generated image.
2. Re-run the verifier. The `media write→serve` line should flip from **WARN
   (bucket empty)** to **PASS** (`<key> serves 200 via CDN`).
3. Evidence: the verifier's PASS line **and** `aws s3 ls s3://lingosai-production-media/ --recursive | head`.
   - If the object lands in S3 but the CDN HEAD is **403/404**, the
     CloudFront origin-access / bucket policy is wrong — that's a real fix, file
     it as a finding (don't tick the box).

### Row 6 — Signup + OTP email
1. Sign up with a **fresh external** email (not a previously-verified address).
2. Confirm the OTP/verification email **arrives** and the code works.
   - ⚠️ Prod is `EMAIL_PROVIDER=ses` and SES production access was **denied**
     (sandbox only → mail to *unverified* externals is dropped). If nothing
     arrives, this is **G5**, not a row-6 bug: flip to Resend (see
     `POLISHED_PRODUCTION_PLAN.md` §G5) and retry.
3. Evidence: screenshot of the received email + successful login.

### Row 7 — Google OAuth
1. Click "Continue with Google" on `www`; complete the Google consent screen.
2. Confirm you land logged-in, then **hard-refresh** — you stay logged in.
3. Evidence: screenshot of the consent screen + the logged-in dashboard after refresh.
   - Prod redirect URI is `https://api.lingosai.com/auth/google/callback` — if
     Google shows a `redirect_uri_mismatch`, add that exact URI in the Google
     Cloud console OAuth client (founder console action).

### Row 8 — Learning-session WebSocket
1. Start a daily session on `www`. Open DevTools → Network → WS.
2. Confirm a WebSocket connects and streams `learning_session.event.v1` frames
   as the lesson advances (teaching → task → feedback).
3. Evidence: screenshot of the WS frames in DevTools.

### Row 9 — Scoring engine
1. Complete one graded activity in that session through to the scorecard.
2. Check the dashboard score / SkillPoints moved.
3. Evidence: scorecard screenshot + before/after dashboard score.

### Row 10 — Pronunciation (Azure)
1. Do a pronunciation activity; record and submit.
2. Confirm a pronunciation score returns (not an error).
3. Evidence: screenshot of the returned score.

### Row 11 — Deepgram streaming STT
1. Use the A2Z speaking widget; speak and confirm a live transcript appears.
2. Evidence: screenshot of the transcript.

### Row 12 — RAG feedback memory (Pinecone)
1. Across **two** sessions, repeat the same kind of mistake.
2. Confirm the second session's feedback references the recurring weakness.
3. Evidence: screenshot of the repeat-weakness feedback.

### Row 13 — Billing + Admin/audit + AI-cost
1. **Razorpay:** make a **test-mode** purchase; confirm entitlement is granted
   and the webhook is received/verified (check backend logs).
2. **Admin/audit:** perform an admin mutation; confirm it appears in the audit log.
3. **AI-cost:** open `/admin/ai-costs`; confirm non-zero spend once AI traffic flowed.
4. Evidence: purchase confirmation + entitlement, audit-log row, AI-cost screenshot.

---

## Definition of done for G4
- `scripts/verify-prod-parity.sh` exits 0 with **media write→serve = PASS**
  (i.e. row 5 finished after a real session), **and**
- every [FOUNDER] row 6–13 box ticked with its evidence attached.

Until then, G4 is **partially** done: the env-driven / infra rows are CLI-proven;
the human-driven rows remain founder actions.
