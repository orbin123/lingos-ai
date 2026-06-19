# LingosAI — Terraform (Phase 3 AWS infrastructure)

Infrastructure-as-code for the backend's AWS substrate. The frontend is on
Vercel (AD-1) and is **not** managed here. Full operational walkthrough:
[`docs/AWS_SETUP.md`](../../docs/AWS_SETUP.md).

## Layout

```
bootstrap/            # run ONCE: S3 state bucket + DynamoDB lock (local state)
modules/
  network/            # VPC, 2 public + 2 private subnets, 1 NAT, 4 security groups
  data/               # RDS Postgres + ElastiCache Redis (private subnets)
  media/              # public S3 + CloudFront (OAC) + separate private S3 (learner audio)
  secrets/            # Secrets Manager: TF-owned DATABASE_URL/REDIS_URL + empty app-secret entries
  email/              # SES domain identity + DKIM (created in the primary env only)
  tls/                # ACM cert for api.<domain>, DNS-validated (Phase 4)
  alb/                # ALB + target group (/health/ready) + listeners (HTTP, or HTTPS once enabled)
  compute/            # ECR, ECS cluster, IAM roles, backend + migration task defs, service
  observability/      # SNS topic + high-signal CloudWatch alarms
  cicd/               # GitHub OIDC provider + least-privilege deploy role
  stack/              # composes all modules — the per-environment unit
envs/
  staging/            # thin root: provider + S3 backend + module "stack" (single-AZ, cheap)
  production/         # thin root: Multi-AZ, deletion protection, owns OIDC + SES identity
```

## Apply order (first time)

```bash
# 0. bootstrap the state backend (once per account)
terraform -chdir=infra/terraform/bootstrap init
terraform -chdir=infra/terraform/bootstrap apply

# 1. production FIRST (it creates the account-global OIDC provider + SES identity)
export TF_VAR_db_password="$(openssl rand -base64 24)"   # store it in a secret too
terraform -chdir=infra/terraform/envs/production init
terraform -chdir=infra/terraform/envs/production plan      # review before apply
terraform -chdir=infra/terraform/envs/production apply

# 2. staging (references the OIDC provider + SES identity created above)
terraform -chdir=infra/terraform/envs/staging init
terraform -chdir=infra/terraform/envs/staging apply
```

`terraform plan` is free and read-only — run it first; it surfaces any typo
before a single resource is created. Then populate Secrets Manager and wire the
GitHub repo variables from `terraform output`. See `docs/AWS_SETUP.md`.

> **Always pass the same `TF_VAR_db_password` (RDS master password) and
> `TF_VAR_alert_email` on every apply.** Omitting `alert_email` destroys the
> CloudWatch alert SNS subscription; omitting `db_password` fails the plan. The
> password is also embedded in the `lingosai/<env>/DATABASE_URL` secret if you
> need to recover it.

## Phase 4 — `api.<domain>` TLS (HTTP → HTTPS)

DNS is at Namecheap (AD-7), so the ACM validation records are published by hand.
The ALB stays HTTP-only until the cert ISSUES, then flips to HTTPS:443 with an
HTTP:80 → 443 redirect. `production` sets `create_api_certificate = true` +
`api_domain = "api.lingosai.com"`.

```bash
cd infra/terraform/envs/production
export TF_VAR_db_password=...   # see note above
export TF_VAR_alert_email=...

# 1. Create ONLY the cert (does not touch the ALB yet).
terraform apply -target='module.stack.module.tls.aws_acm_certificate.api[0]'

# 2. Read the validation CNAME and publish it at Namecheap (Advanced DNS).
terraform output api_certificate_validation_records
#    Also publish at Namecheap now: the `api` CNAME -> the ALB DNS name
#    (terraform output alb_dns_name) and all SES records (ses_* outputs).

# 3. Once the validation CNAME has propagated, finish the apply. The validation
#    resource waits for ACM to issue, then the ALB serves HTTPS:443.
terraform apply
```

Verify: `curl -sI https://api.lingosai.com/health` returns 200, and
`curl -sI http://api.lingosai.com/health` returns a 301 to https.
