# Stack — the full per-environment composition.
#
# staging/ and production/ are thin roots (provider + backend + tfvars) that
# call this module. Everything that differs between them is a variable
# (sizing, multi-AZ, deletion protection, secrets, domains); the wiring is
# identical, so the two environments can't drift in shape.

locals {
  # Non-secret env injected into the backend container. Secrets (DATABASE_URL,
  # API keys, ...) come from the secrets module via the task `secrets` block.
  # These values satisfy the config.py production guard.
  backend_env = {
    ENVIRONMENT      = "production" # staging runs the prod guard too (plan §1.7)
    DEBUG            = "false"
    SQL_ECHO         = "false"
    LOG_LEVEL        = "info"
    STRICT_CONTRACTS = "true"
    DEV_OTP_BYPASS   = "false"

    AUTH_COOKIE_SECURE  = "true"
    CORS_ORIGINS        = var.cors_origins
    FRONTEND_URL        = var.frontend_url
    GOOGLE_REDIRECT_URI = var.google_redirect_uri

    EMAIL_PROVIDER          = "ses"
    SES_REGION              = var.region
    EMAIL_FROM              = var.email_from
    CONTACT_RECIPIENT_EMAIL = var.contact_email

    STORAGE_BACKEND         = "s3"
    MEDIA_S3_BUCKET         = module.media.public_bucket
    MEDIA_PRIVATE_S3_BUCKET = module.media.private_bucket
    MEDIA_S3_REGION         = var.region
    MEDIA_CDN_URL           = "https://${module.media.cdn_domain_name}"

    PINECONE_INDEX_NAME = var.pinecone_index_name
    PINECONE_CLOUD      = "aws"
    PINECONE_REGION     = "us-east-1"
    AZURE_SPEECH_REGION = var.azure_speech_region

    LANGCHAIN_TRACING_V2  = "false" # data-residency: off until decided (plan §1.12)
    AI_RATE_LIMIT_ENABLED = "true"
  }

  # The ALB serves HTTPS from either the TF-managed cert (create_api_certificate)
  # or a supplied ARN. `api_https_enabled` is a *static* bool (not derived from a
  # known-after-apply ARN) so the listener count is determinable at plan time.
  api_certificate_arn = var.create_api_certificate ? module.tls.certificate_arn : var.api_acm_certificate_arn
  api_https_enabled   = var.create_api_certificate || var.api_acm_certificate_arn != ""
}

module "network" {
  source      = "../network"
  environment = var.environment
  vpc_cidr    = var.vpc_cidr
  app_port    = var.app_port
}

module "data" {
  source             = "../data"
  environment        = var.environment
  private_subnet_ids = module.network.private_subnet_ids
  rds_sg_id          = module.network.rds_sg_id
  redis_sg_id        = module.network.redis_sg_id

  db_password           = var.db_password
  multi_az              = var.multi_az
  deletion_protection   = var.deletion_protection
  skip_final_snapshot   = var.skip_final_snapshot
  db_instance_class     = var.db_instance_class
  redis_node_type       = var.redis_node_type
  backup_retention_days = var.backup_retention_days
}

module "media" {
  source                  = "../media"
  environment             = var.environment
  cdn_acm_certificate_arn = var.cdn_acm_certificate_arn
  cdn_domain_aliases      = var.cdn_domain_aliases
}

module "secrets" {
  source        = "../secrets"
  environment   = var.environment
  db_username   = var.db_username
  db_password   = var.db_password
  rds_address   = module.data.rds_address
  rds_port      = module.data.rds_port
  db_name       = module.data.db_name
  redis_address = module.data.redis_primary_endpoint
  redis_port    = module.data.redis_port
}

module "email" {
  source = "../email"
  domain = var.email_domain
  create = var.create_ses_identity
}

module "tls" {
  source     = "../tls"
  create     = var.create_api_certificate
  api_domain = var.api_domain
}

module "alb" {
  source                     = "../alb"
  environment                = var.environment
  vpc_id                     = module.network.vpc_id
  public_subnet_ids          = module.network.public_subnet_ids
  alb_sg_id                  = module.network.alb_sg_id
  app_port                   = var.app_port
  certificate_arn            = local.api_certificate_arn
  enable_https               = local.api_https_enabled
  enable_deletion_protection = var.deletion_protection
}

module "compute" {
  source                   = "../compute"
  environment              = var.environment
  app_port                 = var.app_port
  private_subnet_ids       = module.network.private_subnet_ids
  ecs_sg_id                = module.network.ecs_sg_id
  target_group_arn         = module.alb.target_group_arn
  secret_arns              = module.secrets.secret_arns
  all_secret_arns          = module.secrets.all_secret_arns
  environment_variables    = local.backend_env
  media_public_bucket_arn  = module.media.public_bucket_arn
  media_private_bucket_arn = module.media.private_bucket_arn
  image_tag                = var.image_tag
  task_cpu                 = var.task_cpu
  task_memory              = var.task_memory
  desired_count            = var.desired_count

  # The target group must be wired to a listener before the service registers.
  depends_on = [module.alb]
}

module "observability" {
  source                     = "../observability"
  environment                = var.environment
  alert_email                = var.alert_email
  alb_arn_suffix             = module.alb.alb_arn_suffix
  target_group_arn_suffix    = module.alb.target_group_arn_suffix
  cluster_name               = module.compute.cluster_name
  service_name               = module.compute.service_name
  db_instance_id             = module.data.db_instance_id
  redis_replication_group_id = module.data.redis_replication_group_id
}

module "cicd" {
  source               = "../cicd"
  environment          = var.environment
  github_repo          = var.github_repo
  create_oidc_provider = var.create_oidc_provider
  ecr_repository_arn   = module.compute.ecr_repository_arn
  passable_role_arns   = [module.compute.task_role_arn, module.compute.execution_role_arn]
}
