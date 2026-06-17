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
      Environment = "staging"
      ManagedBy   = "terraform"
    }
  }
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "alert_email" {
  type    = string
  default = ""
}

module "stack" {
  source      = "../../modules/stack"
  environment = "staging"
  region      = var.region

  # Cost-optimized: single-AZ, no deletion protection, skip final snapshot.
  multi_az            = false
  deletion_protection = false
  skip_final_snapshot = true
  db_instance_class   = "db.t4g.micro"
  redis_node_type     = "cache.t4g.micro"
  desired_count       = 1

  # Distinct CIDR from production keeps the two VPCs tidy (and peerable later).
  vpc_cidr = "10.1.0.0/16"

  db_password = var.db_password

  cors_origins        = "https://www-staging.lingosai.com"
  frontend_url        = "https://www-staging.lingosai.com"
  google_redirect_uri = "https://api-staging.lingosai.com/auth/google/callback"
  email_domain        = "lingosai.com"
  email_from          = "LingosAI Staging <noreply@lingosai.com>"
  contact_email       = "support@lingosai.com"

  alert_email = var.alert_email

  github_repo          = "orbin123/lingos-ai"
  create_oidc_provider = false # production owns the account-global OIDC provider
}
