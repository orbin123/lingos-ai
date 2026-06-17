# AWS_SETUP.md — Phase 3 founder runbook

> Companion to [`complete_production_plan.md`](./complete_production_plan.md) §Phase 3,
> [`DEPLOY.md`](./DEPLOY.md), and the Terraform in [`infra/terraform/`](../infra/terraform).
> This is the **account-side** sequence — the things the coding agent could not do for you because
> they touch the live AWS account. Region: **us-east-1**. Do the steps in order.

Everything in `infra/terraform/` and the app code (`S3BlobStorage`, the `ses` email provider,
`deploy.yml`) is already written and reviewed. Your job here is: grant Terraform permission, create
the state backend, run `plan`/`apply`, fill in secrets, verify the domain for SES, and wire the
GitHub repo variables. `terraform plan` is free and read-only — run it first at every step.

---

## 0. Prerequisites

- AWS CLI authenticated as a principal that can create infra (see step 1).
- `terraform >= 1.5`, `jq`, `openssl` installed locally.
- The repo cloned; commands below assume you run them from the repo root.

---

## 1. Grant Terraform permission

The `lingos-ai-cli` user (or a dedicated `terraform` user) needs broad create permissions for the
first apply. Simplest path: attach **AdministratorAccess** temporarily, then scope it down once the
stack exists.

```bash
aws iam attach-user-policy --user-name lingos-ai-cli \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
```

> Scope-down later: the ongoing deploy uses the OIDC role Terraform creates (least-privilege), not
> this user. After the first successful apply you can replace AdministratorAccess with a tighter
> policy and re-apply only when you change infra.

---

## 2. Bootstrap the Terraform state backend (once per account)

```bash
terraform -chdir=infra/terraform/bootstrap init
terraform -chdir=infra/terraform/bootstrap apply
```

This creates the **versioned** S3 state bucket (`lingosai-terraform-state`) and the DynamoDB lock
table (`lingosai-terraform-locks`). If those names are taken, change them in
`bootstrap/variables.tf` **and** the `backend "s3"` blocks in `envs/*/backend.tf`.

---

## 3. Apply production (creates the shared OIDC provider + SES identity)

Production must apply **before** staging — it owns the account-global GitHub OIDC provider and the
shared SES domain identity that staging references.

```bash
# RDS master password — generate once, keep a copy in your password manager.
export TF_VAR_db_password="$(openssl rand -base64 24)"
export TF_VAR_alert_email="you@example.com"   # SNS alarm destination

terraform -chdir=infra/terraform/envs/production init
terraform -chdir=infra/terraform/envs/production plan      # REVIEW carefully
terraform -chdir=infra/terraform/envs/production apply
```

> If `terraform plan` flags an unavailable RDS/Redis engine version, bump `postgres_version` /
> `redis_version` in `modules/data/variables.tf` to a version AWS offers in us-east-1.

Capture the outputs — you'll need them in steps 5–6:

```bash
terraform -chdir=infra/terraform/envs/production output
```

---

## 4. Populate Secrets Manager

Terraform created `DATABASE_URL` and `REDIS_URL` with real values (derived from the RDS/Redis
endpoints). The **app secrets** were created empty (placeholder `REPLACE_ME`) — fill each with the
real value once. Re-applies will not clobber them.

```bash
ENV=production
put() { aws secretsmanager put-secret-value --secret-id "lingosai/$ENV/$1" --secret-string "$2"; }

put JWT_SECRET            "$(openssl rand -hex 32)"
put OTP_HASHING_SECRET    "$(openssl rand -hex 32)"   # MUST differ from JWT_SECRET
put OPENAI_API_KEY        "sk-..."
put PINECONE_API_KEY      "..."
put AZURE_SPEECH_KEY      "..."
put DEEPGRAM_API_KEY      "..."
put GOOGLE_CLIENT_ID      "..."
put GOOGLE_CLIENT_SECRET  "..."
put RAZORPAY_KEY_ID       "..."     # live keys (Phase 4)
put RAZORPAY_KEY_SECRET   "..."
put RAZORPAY_WEBHOOK_SECRET "..."
put SENTRY_DSN            "https://...ingest.sentry.io/..."
put LANGCHAIN_API_KEY     "..."
```

The ECS task injects every one of these as an env var via its `secrets` block — the app reads them
as ordinary environment variables. After filling them, force a new deployment (step 8) so tasks pick
them up.

---

## 5. SES — verify the domain + leave the sandbox (do this EARLY)

Terraform created the SES domain identity + DKIM keys but **cannot** verify ownership (that's DNS,
published in Phase 4) or exit the sandbox (an account-level console request). Start both now —
sandbox exit takes AWS ~24h.

1. **Request production access:** SES console → *Account dashboard* → *Request production access*.
2. **Publish DNS records** (Phase 4, at your registrar) from the Terraform outputs:
   - `ses_verification_token` → TXT at `_amazonses.lingosai.com`.
   - each `ses_dkim_tokens` value `T` → CNAME `T._domainkey.lingosai.com` → `T.dkim.amazonses.com`.
   - MAIL FROM (`mail.lingosai.com`): MX `10 feedback-smtp.us-east-1.amazonses.com` + SPF TXT
     `v=spf1 include:amazonses.com ~all`.
   - DMARC (recommended): TXT at `_dmarc.lingosai.com` → `v=DMARC1; p=none; rua=mailto:dmarc@lingosai.com`.

Until verified + out of sandbox, SES only delivers to verified addresses — fine for a test send,
not for real users.

---

## 6. Wire GitHub Environments for `deploy.yml`

In GitHub → *Settings → Environments*, create **`production`** (and later `staging`) and add these
**variables** from `terraform output`:

| GitHub variable | Terraform output |
|---|---|
| `AWS_REGION` | `us-east-1` |
| `AWS_DEPLOY_ROLE_ARN` | `github_deploy_role_arn` |
| `ECR_REPOSITORY` | `ecr_repository_url` (full URL) |
| `ECS_CLUSTER` | `ecs_cluster_name` |
| `ECS_SERVICE` | `ecs_service_name` |
| `ECS_TASK_FAMILY` | `backend_task_family` |
| `ECS_MIGRATE_FAMILY` | `migrate_task_family` |
| `ECS_SUBNETS` | `ecs_subnet_ids` (comma-separated, no spaces) |
| `ECS_SECURITY_GROUP` | `ecs_security_group_id` |
| `HEALTHCHECK_URL` | `http://<alb_dns_name>/health/ready` (Phase 4: `https://api.lingosai.com/health/ready`) |

> The baseline ECS service runs the `:latest` image placeholder until the first `deploy.yml` run
> pushes a real `git-<sha>` image and rolls it out.

---

## 7. Apply staging (optional but recommended)

```bash
export TF_VAR_db_password="$(openssl rand -base64 24)"   # distinct from prod
terraform -chdir=infra/terraform/envs/staging init
terraform -chdir=infra/terraform/envs/staging apply
```

Repeat steps 4 + 6 for `ENV=staging` and a `staging` GitHub Environment.

---

## 8. First deploy + validation drills

Run the CD pipeline: GitHub → *Actions → deploy → Run workflow* → pick `production` (or `staging`).
It builds the image, runs migrations as a one-off task, rolls out the service, and smoke-checks
`/health/ready`.

Then walk the Phase 3 validation checklist (`complete_production_plan.md`):

- [ ] `terraform plan` clean for both envs.
- [ ] Backend task healthy on Fargate; ALB target healthy on `/health/ready`.
- [ ] RDS **not** reachable from the public internet (`nc -zv <rds-endpoint> 5432` from your laptop
      should time out).
- [ ] Migration one-off task ran `alembic upgrade head` successfully (CloudWatch `/ecs/...-backend`,
      stream prefix `migrate`).
- [ ] A real TTS/image generation writes to **S3** and serves via CloudFront (not local disk).
- [ ] A test email sends via SES (after sandbox exit) to an external address.
- [ ] A secret rotated in Secrets Manager is picked up after a redeploy.
- [ ] An RDS snapshot restore drill completes within the RTO target (`RUNBOOK.md`).

---

## Rollback (keep handy)

```bash
# Re-point the service at the previous task-def revision (previous image sha).
aws ecs update-service --cluster <ECS_CLUSTER> --service <ECS_SERVICE> \
  --task-definition <ECS_TASK_FAMILY>:<previous-revision>
aws ecs wait services-stable --cluster <ECS_CLUSTER> --services <ECS_SERVICE>
```

Frontend rollback is one click in Vercel (*Deployments → previous → Promote to Production*).

---

## What's left for Phase 4 (domain/DNS/SSL)

- Request the ACM cert for `api.lingosai.com` (us-east-1), DNS-validate it, then set
  `api_acm_certificate_arn` (and `cdn_acm_certificate_arn` + `cdn_domain_aliases` for a custom media
  domain) in the env root and re-apply — that flips the ALB to HTTPS:443.
- Publish the SES DNS records from step 5 and the Vercel/ALB records.
- Update `HEALTHCHECK_URL`, `CORS_ORIGINS`, `FRONTEND_URL`, `GOOGLE_REDIRECT_URI` to the real hosts.
