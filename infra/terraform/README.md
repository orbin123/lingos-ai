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
  alb/                # ALB + target group (/health/ready) + listeners (HTTPS in Phase 4)
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
