# G6 — Observability finish runbook

> **Gap G6** of [`POLISHED_PRODUCTION_PLAN.md`](./POLISHED_PRODUCTION_PLAN.md) (Phase C).
> Closes the launch items: *forced error captured end-to-end in Sentry (with a trace id
> matching CloudWatch), one CloudWatch alarm delivered to the founder, and the
> `/health/ready` 503 path observed.*
>
> ⚠️ `docs/` is git-ignored — force-add: `git add -f docs/G6_OBSERVABILITY_RUNBOOK.md`.

All commands assume `--region us-east-1`, account `924903313980`, and the `lingos-ai-cli`
credentials.

---

## What the code PR already did (`feat/g6-observability`)

| Change | File | Effect |
|---|---|---|
| `_before_send` now tags **every** Sentry event with the request `trace_id` | `backend/app/core/sentry.py` | Auto-captured unhandled 500s (real prod bugs) are now correlatable to the CloudWatch log line / `AIRequestLog` by `trace_id`, not just manually-swallowed ones |
| New super-admin route `POST /admin/observability/test-error` | `backend/app/modules/admin/routes.py` | Deterministic, safe way to force a real 500 → Sentry capture; returns the `trace_id` in the body and logs it (`observability_test_error`) for cross-referencing |
| Unit + integration tests; regenerated `openapi.json` | `backend/tests/...`, `backend/openapi.json` | Covers the new behaviour; keeps the contract/openapi-drift gate green |

**Already in place before this PR (verified, no change needed):** backend + frontend Sentry
init gated on the DSN; `SENTRY_DSN` secret wired end-to-end (Secrets Manager → task-def →
app); 11 CloudWatch alarms + the `lingosai-production-alerts` SNS topic + email subscription;
the `/health/ready` 503 path and ALB health check.

### ⚠️ Sentry: only the secret **value** is missing — no task-def revision needed

Unlike G5 (which *added* a new secret), `SENTRY_DSN`'s ARN is **already referenced** in the
live task-def `secrets` block. So you only need to (a) make sure the secret holds a real DSN
(not the `REPLACE_ME` placeholder) and (b) force a new deployment so containers re-resolve it
at start. **No task-def revision is required.**

---

## Founder steps (in order)

### 1. Backend — ensure `SENTRY_DSN` holds a real value
Check the current value (a DSN is not high-sensitivity — it's embedded in the frontend bundle
anyway):
```bash
aws secretsmanager get-secret-value \
  --secret-id lingosai/production/SENTRY_DSN \
  --region us-east-1 --query SecretString --output text
```
If it is `REPLACE_ME` / empty, set the real backend DSN (Sentry → project → Settings → Client
Keys (DSN)):
```bash
aws secretsmanager put-secret-value \
  --secret-id lingosai/production/SENTRY_DSN \
  --secret-string 'https://<key>@<org>.ingest.us.sentry.io/<project>' \
  --region us-east-1

# Containers read secrets at start → force a fresh deployment to pick up the new value.
aws ecs update-service --cluster lingosai-production \
  --service lingosai-production-backend --force-new-deployment --region us-east-1
aws ecs wait services-stable --cluster lingosai-production \
  --services lingosai-production-backend --region us-east-1
```

### 2. Frontend — set `NEXT_PUBLIC_SENTRY_DSN` in Vercel
- Vercel → project → **Settings → Environment Variables** → add `NEXT_PUBLIC_SENTRY_DSN`
  (Production) = the frontend Sentry DSN.
- (Optional) `SENTRY_AUTH_TOKEN`, `SENTRY_ORG`, `SENTRY_PROJECT` to enable source-map upload
  (`next.config.ts` skips upload when the token is absent).
- Redeploy production (push to `main` or "Redeploy" the latest).

### 3. Prove forced-error capture end-to-end (the core G6 verification)
Get a **super-admin** bearer token (log in on `www` as a super-admin and copy the JWT, or mint
one), then:
```bash
curl -i -X POST https://api.lingosai.com/admin/observability/test-error \
  -H "Authorization: Bearer <SUPER_ADMIN_JWT>"
```
Expect **HTTP 500** with a body like `{"status":"error","detail":"...","trace_id":"<hex>"}`.
Then confirm the **same `trace_id`** appears in both places:
- **Sentry** → Issues → the new "G6 observability self-test" event → tag `trace_id = <hex>`.
- **CloudWatch** → the backend log group → filter for the `trace_id` (the `observability_test_error`
  line and the `http_request` access line both carry it).

This satisfies *"Force a 500 and confirm it appears in Sentry with a trace id matching CloudWatch."*
A single 500 is far under the `alb_5xx` alarm threshold (>10 in 60s), so it will not page you.

> Frontend capture check (optional): trigger a client error on `www` (e.g. a deliberate throw in
> a dev build, or any real runtime error) and confirm it lands in the Sentry frontend project.

### 4. Confirm the SNS alarm subscription + deliver one alarm
Check the email subscription is **confirmed** (not `PendingConfirmation`):
```bash
TOPIC_ARN=$(aws sns list-topics --region us-east-1 \
  --query "Topics[?contains(TopicArn, 'lingosai-production-alerts')].TopicArn" --output text)
aws sns list-subscriptions-by-topic --topic-arn "$TOPIC_ARN" --region us-east-1 \
  --query "Subscriptions[].{Endpoint:Endpoint,Arn:SubscriptionArn}" --output table
```
- If `Arn` shows `PendingConfirmation`, open the **"AWS Notification - Subscription Confirmation"**
  email and click **Confirm subscription**. (If no subscription exists, re-run
  `terraform apply` in `envs/production` with `TF_VAR_alert_email` set — omitting it destroys the
  subscription; see `docs/AWS_SETUP.md`.)

Then fire one alarm to prove delivery reaches your inbox (auto-resets):
```bash
aws cloudwatch set-alarm-state --region us-east-1 \
  --alarm-name lingosai-production-alb-5xx \
  --state-value ALARM \
  --state-reason "G6 alert-delivery test"
```
Confirm the alarm email arrives. (List exact alarm names with
`aws cloudwatch describe-alarms --region us-east-1 --query "MetricAlarms[].AlarmName" --output table`.)

### 5. Observe the `/health/ready` → 503 resilience path
**Safe option (recommended):** prove the SNS/alarm path for unhealthy targets without touching the
DB by forcing the alarm state:
```bash
aws cloudwatch set-alarm-state --region us-east-1 \
  --alarm-name lingosai-production-alb-unhealthy \
  --state-value ALARM --state-reason "G6 503-path test"
```
**Faithful option (more invasive):** temporarily make `/health/ready` return 503 (e.g. block the
backend SG from RDS for a moment, or stop Redis), then watch the ALB target group flip to
`unhealthy` and recover:
```bash
TG_ARN=$(aws elbv2 describe-target-groups --region us-east-1 \
  --query "TargetGroups[?contains(TargetGroupName,'lingosai')].TargetGroupArn" --output text)
aws elbv2 describe-target-health --target-group-arn "$TG_ARN" --region us-east-1 \
  --query "TargetHealthDescriptions[].TargetHealth.State" --output table
```
Restore connectivity and confirm the target returns to `healthy`. *(Do this in a quiet window — a
single healthy task means a real 503 briefly removes the only target.)*

---

## Definition of done for G6
- [ ] `SENTRY_DSN` secret holds a real value (not `REPLACE_ME`); backend redeployed.
- [ ] `NEXT_PUBLIC_SENTRY_DSN` set in Vercel; frontend redeployed.
- [ ] `POST /admin/observability/test-error` → 500; the returned `trace_id` is visible on the
      Sentry event **and** in CloudWatch (evidence captured).
- [ ] SNS email subscription **confirmed**; one alarm delivered to the founder's inbox.
- [ ] `/health/ready` 503 path observed (target flips unhealthy, or the `alb-unhealthy` alarm fires).

## Notes / rollback
- The test-error route is **super-admin only** and idempotent; nothing to roll back. It can stay in
  prod as a permanent self-test, or be removed later — it is not load-bearing.
- `set-alarm-state` is transient: CloudWatch re-evaluates on the next datapoint and returns the
  alarm to its real state automatically.
- If you'd rather not keep a forced-error endpoint in prod, the `_before_send` `trace_id` tagging
  alone still delivers the real value (correlating genuine 500s to CloudWatch); the route is only a
  verification convenience.
