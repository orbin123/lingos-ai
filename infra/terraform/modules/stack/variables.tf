variable "environment" {
  description = "staging | production"
  type        = string
}

variable "region" {
  type    = string
  default = "us-east-1"
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

# --- Data sizing (prod vs staging) -----------------------------------------
variable "db_username" {
  type    = string
  default = "lingosai"
}

variable "db_password" {
  description = "RDS master password. Pass via TF_VAR_db_password from a secret, not committed."
  type        = string
  sensitive   = true
}

variable "multi_az" {
  type    = bool
  default = false
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "skip_final_snapshot" {
  type    = bool
  default = false
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.small"
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}

variable "backup_retention_days" {
  type    = number
  default = 7
}

# --- Compute sizing ---------------------------------------------------------
variable "image_tag" {
  type    = string
  default = "latest"
}

variable "task_cpu" {
  type    = number
  default = 512
}

variable "task_memory" {
  type    = number
  default = 1024
}

variable "desired_count" {
  type    = number
  default = 1
}

# --- App config (env-specific hostnames) -----------------------------------
variable "cors_origins" {
  description = "Allowed frontend origin(s). No localhost in prod."
  type        = string
}

variable "frontend_url" {
  type = string
}

variable "google_redirect_uri" {
  type = string
}

variable "email_from" {
  type    = string
  default = "LingosAI <noreply@lingosai.com>"
}

variable "contact_email" {
  type    = string
  default = "support@lingosai.com"
}

variable "email_domain" {
  description = "SES sending domain."
  type        = string
  default     = "lingosai.com"
}

variable "pinecone_index_name" {
  type    = string
  default = "lingosai-responses"
}

variable "azure_speech_region" {
  type    = string
  default = "eastus"
}

# --- TLS / CDN custom domains (set in Phase 4) ------------------------------
variable "api_acm_certificate_arn" {
  description = "ACM cert for api.<domain>. Empty = ALB serves HTTP only (Phase 3)."
  type        = string
  default     = ""
}

variable "cdn_acm_certificate_arn" {
  description = "ACM cert (us-east-1) for a custom media CDN domain. Empty until Phase 4."
  type        = string
  default     = ""
}

variable "cdn_domain_aliases" {
  type    = list(string)
  default = []
}

# --- Observability + CI/CD --------------------------------------------------
variable "alert_email" {
  type    = string
  default = ""
}

variable "github_repo" {
  description = "owner/repo for the OIDC deploy role."
  type        = string
}

variable "create_oidc_provider" {
  description = "Create the account-global GitHub OIDC provider in this env (true in exactly one)."
  type        = bool
  default     = false
}

variable "create_ses_identity" {
  description = "Create the shared SES domain identity in this env (true in exactly one)."
  type        = bool
  default     = false
}
