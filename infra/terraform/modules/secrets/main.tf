# Secrets — one Secrets Manager entry per sensitive value.
#
# Split in two:
#   * Terraform-owned: DATABASE_URL and REDIS_URL are derived from data-tier
#     outputs (endpoints) + the DB password, so Terraform writes the value.
#     The app reads the plain postgresql:// URL (database.py adds +psycopg).
#     Redis has transit encryption on -> rediss:// .
#   * Founder-owned: API keys / app secrets are created EMPTY here; the founder
#     puts the real values once (see docs/AWS_SETUP.md). Terraform never sees
#     them, and re-applies don't clobber them (ignore_changes on the version).
#
# The ECS task definition injects every one of these as an env var via its
# `secrets` block — the app reads them as ordinary environment variables.

locals {
  name_prefix = "lingosai-${var.environment}"
  prefix      = "lingosai/${var.environment}"

  # App secrets the founder fills in once after the first apply.
  founder_secret_names = toset([
    "JWT_SECRET",
    "OTP_HASHING_SECRET",
    "OPENAI_API_KEY",
    "PINECONE_API_KEY",
    "AZURE_SPEECH_KEY",
    "DEEPGRAM_API_KEY",
    "GOOGLE_CLIENT_ID",
    "GOOGLE_CLIENT_SECRET",
    "RAZORPAY_KEY_ID",
    "RAZORPAY_KEY_SECRET",
    "RAZORPAY_WEBHOOK_SECRET",
    "SENTRY_DSN",
    "LANGCHAIN_API_KEY",
  ])
}

# --- Terraform-owned connection strings ------------------------------------

resource "aws_secretsmanager_secret" "database_url" {
  name = "${local.prefix}/DATABASE_URL"
  tags = { Name = "${local.name_prefix}-DATABASE_URL" }
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id = aws_secretsmanager_secret.database_url.id
  secret_string = format(
    "postgresql://%s:%s@%s:%d/%s",
    var.db_username,
    var.db_password,
    var.rds_address,
    var.rds_port,
    var.db_name,
  )
}

resource "aws_secretsmanager_secret" "redis_url" {
  name = "${local.prefix}/REDIS_URL"
  tags = { Name = "${local.name_prefix}-REDIS_URL" }
}

resource "aws_secretsmanager_secret_version" "redis_url" {
  secret_id     = aws_secretsmanager_secret.redis_url.id
  secret_string = format("rediss://%s:%d/0", var.redis_address, var.redis_port)
}

# --- Founder-owned app secrets (created empty) ------------------------------

resource "aws_secretsmanager_secret" "app" {
  for_each = local.founder_secret_names
  name     = "${local.prefix}/${each.key}"
  tags     = { Name = "${local.name_prefix}-${each.key}" }
}

# Seed an empty placeholder version so the secret resolves, then never touch it
# again — the founder's `put-secret-value` is the source of truth.
resource "aws_secretsmanager_secret_version" "app_placeholder" {
  for_each      = local.founder_secret_names
  secret_id     = aws_secretsmanager_secret.app[each.key].id
  secret_string = "REPLACE_ME"

  lifecycle {
    ignore_changes = [secret_string]
  }
}
