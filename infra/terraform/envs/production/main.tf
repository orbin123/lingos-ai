terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project     = "lingosai"
      Environment = "production"
      ManagedBy   = "terraform"
    }
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

# RDS master password — supply via `export TF_VAR_db_password=...` from a
# generated secret (openssl rand). Never commit it.
variable "db_password" {
  type      = string
  sensitive = true
}

module "stack" {
  source      = "../../modules/stack"
  environment = "production"
  region      = var.region

  # HA + safety for production.
  multi_az            = true
  deletion_protection = true
  skip_final_snapshot = false
  db_instance_class   = "db.t4g.small"
  redis_node_type     = "cache.t4g.micro"
  desired_count       = 1

  db_password = var.db_password

  # Real production hostnames.
  cors_origins        = "https://www.lingosai.com"
  frontend_url        = "https://www.lingosai.com"
  google_redirect_uri = "https://api.lingosai.com/auth/google/callback"
  email_domain        = "lingosai.com"
  email_from          = "LingosAI <noreply@lingosai.com>"
  contact_email       = "support@lingosai.com"

  # Phase 4: request + DNS-validate the ACM cert for api.lingosai.com. Once the
  # validation CNAME is published at Namecheap and the cert ISSUES, the ALB flips
  # to HTTPS:443 with an HTTP->443 redirect.
  create_api_certificate = true
  api_domain             = "api.lingosai.com"

  alert_email        = var.alert_email
  monthly_budget_usd = var.monthly_budget_usd

  github_repo          = "orbin123/lingos-ai"
  create_oidc_provider = true # production owns the account-global OIDC provider
  create_ses_identity  = true # ...and the shared SES domain identity
}

variable "alert_email" {
  type    = string
  default = ""
}

variable "monthly_budget_usd" {
  description = "Monthly AWS cost budget (USD). Override with TF_VAR_monthly_budget_usd."
  type        = number
  default     = 150
}
