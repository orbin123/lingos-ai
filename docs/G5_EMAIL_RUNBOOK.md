# G5 — Email provider runbook (SES → Resend)

> **Gap G5** of [`POLISHED_PRODUCTION_PLAN.md`](./POLISHED_PRODUCTION_PLAN.md). Closes the
> "transactional email reaches an **external** inbox" launch item and directly unblocks
> **G4 row 6** (signup OTP email).
>
> ⚠️ `docs/` is git-ignored — force-add: `git add -f docs/G5_EMAIL_RUNBOOK.md`.

---

## Decision (verified 2026-06-19)

SES production access is **DENIED** — the account is **sandbox-only** and can email *only*
verified identities, never an arbitrary inbox:

```
$ aws sesv2 get-account --region us-east-1
  "ProductionAccessEnabled": false,
  "ReviewDetails": { "Status": "DENIED", "CaseId": "178170275200223" }
```

Per the plan's decision gate, prod therefore sends transactional email via **Resend**
(`EMAIL_PROVIDER=resend`). The backend (`app/email/`) already supports Resend behind that flag;
no app code changes are needed.

---

## What the code/IaC PR already did (`feat/g5-email-resend`)

| Change | File | Effect |
|---|---|---|
| `EMAIL_PROVIDER = "resend"` | `infra/terraform/modules/stack/main.tf` | Desired-state provider is Resend |
| `RESEND_API_KEY` added to `founder_secret_names` | `infra/terraform/modules/secrets/main.tf` | Creates the Secrets Manager entry, wires it into the task-def `secrets` block, **and widens the execution-role `GetSecretValue` grant** |
| Verifier asserts `EMAIL_PROVIDER=resend` + `RESEND_API_KEY` wired | `scripts/verify-prod-parity.sh` | CLI proof once the live flip is done |

### ⚠️ Why Terraform alone does NOT flip live prod

`deploy.yml` builds each new task-def by **cloning the currently-running task-def** (`describe-task-definition`)
and swapping only the image; the compute module sets `lifecycle { ignore_changes = [container_definitions] }`.
So neither `terraform apply` nor a normal code deploy changes the live `environment`/`secrets`.
**The live flip is a one-time founder task-def revision** (Step 5 below); after that, deploy.yml carries
it forward automatically.

There is a **load-bearing ordering dependency**: the execution role can only read secret ARNs in
`all_secret_arns`. So `terraform apply` (Step 3, which creates the secret + widens the grant) **must run
before** the task-def revision that references `RESEND_API_KEY` (Step 5), or the new task fails to start.

---

## Founder steps (in order)

All commands assume `--region us-east-1` and the `lingos-ai-cli` credentials.

### 1. Verify the sending domain in Resend
- Resend dashboard → **Domains → Add Domain** → `lingosai.com` (or a `send.` subdomain).
- Publish the **DKIM + SPF** records Resend shows you at **Namecheap**. These are Resend's own keys —
  **separate** from the existing SES DKIM records; adding them does not disturb SES.
- Wait for Resend to show the domain **Verified**.
- Confirm `EMAIL_FROM` (`LingosAI <noreply@lingosai.com>`) is on the verified domain. *(Until the
  domain verifies, Resend only delivers from `onboarding@resend.dev` to the account owner — not good
  enough for launch.)*

### 2. Create a Resend API key
- Resend → **API Keys → Create** (sending permission). Copy it once.

### 3. Merge the PR, then `terraform apply` (creates the secret + IAM grant)
```bash
# after feat/g5-email-resend is merged to main
cd infra/terraform/envs/production
export TF_VAR_db_password=...        # same as your normal apply
terraform plan      # expect: + secret lingosai/production/RESEND_API_KEY, IAM policy update
terraform apply
```
This creates an **empty** `lingosai/production/RESEND_API_KEY` secret (placeholder `REPLACE_ME`,
`ignore_changes` on the value) and adds its ARN to the execution role's `GetSecretValue` policy.

### 4. Put the real key into Secrets Manager
```bash
aws secretsmanager put-secret-value \
  --secret-id lingosai/production/RESEND_API_KEY \
  --secret-string 're_xxxxxxxxxxxxxxxxxxxxxxxx' \
  --region us-east-1
```

### 5. One-time live flip — register a task-def revision with the new env + secret
Run this once (it reads the current live task-def, sets `EMAIL_PROVIDER=resend`, appends the
`RESEND_API_KEY` secret, registers a new revision, and points the service at it):

```bash
REGION=us-east-1
CLUSTER=lingosai-production
SERVICE=lingosai-production-backend
FAMILY=lingosai-production-backend
SECRET_ARN=$(aws secretsmanager describe-secret \
  --secret-id lingosai/production/RESEND_API_KEY \
  --region "$REGION" --query ARN --output text)

NEW_TD=$(aws ecs describe-task-definition --task-definition "$FAMILY" --region "$REGION" \
  --query taskDefinition | jq \
  --arg ARN "$SECRET_ARN" '
    .containerDefinitions[0].environment =
      ([.containerDefinitions[0].environment[] | select(.name != "EMAIL_PROVIDER")]
       + [{name:"EMAIL_PROVIDER", value:"resend"}])
    | .containerDefinitions[0].secrets =
      ([.containerDefinitions[0].secrets[]? | select(.name != "RESEND_API_KEY")]
       + [{name:"RESEND_API_KEY", valueFrom:$ARN}])
    | {family, taskRoleArn, executionRoleArn, networkMode, containerDefinitions,
       requiresCompatibilities, cpu, memory}')

NEW_ARN=$(aws ecs register-task-definition --cli-input-json "$NEW_TD" --region "$REGION" \
  --query taskDefinition.taskDefinitionArn --output text)
echo "Registered: $NEW_ARN"

aws ecs update-service --cluster "$CLUSTER" --service "$SERVICE" \
  --task-definition "$NEW_ARN" --region "$REGION" >/dev/null
aws ecs wait services-stable --cluster "$CLUSTER" --services "$SERVICE" --region "$REGION"
echo "Service stable on the resend task-def."
```
> Do the same against the **migrate** family (`lingosai-production-migrate`) only if a migration task
> ever needs to send email — it does not, so it can be left as-is.

### 6. Prove it — send a real OTP to an external inbox
- On `https://www.lingosai.com`, sign up with an **external** address you control (Gmail/Outlook —
  *not* an SES-verified identity).
- Confirm the OTP email **arrives** (check spam). This is the G5 / G4-row-6 evidence — screenshot it.
- Optionally check Resend dashboard → **Logs** for the delivery event.

### 7. Re-run the verifier (CLI proof)
```bash
bash scripts/verify-prod-parity.sh
```
Expect `EMAIL_PROVIDER` → **resend** PASS and `secret wiring` PASS (now includes `RESEND_API_KEY`).

---

## Definition of done for G5
- [ ] Resend domain `lingosai.com` verified (DKIM/SPF published).
- [ ] `terraform apply` created `lingosai/production/RESEND_API_KEY` + the IAM grant.
- [ ] Real Resend key stored in Secrets Manager (not `REPLACE_ME`).
- [ ] Live task-def revision flips `EMAIL_PROVIDER=resend` + references `RESEND_API_KEY`; service stable.
- [ ] An OTP email **delivered to an external inbox** (evidence captured).
- [ ] `scripts/verify-prod-parity.sh` → `EMAIL_PROVIDER=resend` + secret wiring PASS.

## Rollback
If Resend misbehaves, re-run Step 5 with `EMAIL_PROVIDER` set back to `ses` (and drop the secret
override) — or, faster, point the service at the previous task-def revision:
`aws ecs update-service --cluster lingosai-production --service lingosai-production-backend --task-definition <prev-arn>`.
SES will still only reach verified identities (sandbox), but it restores the prior behavior.
