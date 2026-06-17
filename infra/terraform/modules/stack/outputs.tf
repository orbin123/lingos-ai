# Everything the founder needs after `apply`: DNS targets (Phase 4), the
# GitHub repo variables for deploy.yml, and the SES DNS records.

output "alb_dns_name" {
  description = "Point api.<domain> here in Phase 4."
  value       = module.alb.alb_dns_name
}

output "alb_zone_id" {
  value = module.alb.alb_zone_id
}

output "cdn_domain_name" {
  description = "CloudFront domain for media (base of MEDIA_CDN_URL)."
  value       = module.media.cdn_domain_name
}

output "media_public_bucket" {
  value = module.media.public_bucket
}

output "media_private_bucket" {
  value = module.media.private_bucket
}

# --- deploy.yml GitHub repo variables --------------------------------------
output "github_deploy_role_arn" {
  description = "GitHub repo variable AWS_DEPLOY_ROLE_ARN."
  value       = module.cicd.deploy_role_arn
}

output "ecr_repository_url" {
  description = "GitHub repo variable ECR_REPOSITORY."
  value       = module.compute.ecr_repository_url
}

output "ecs_cluster_name" {
  description = "GitHub repo variable ECS_CLUSTER."
  value       = module.compute.cluster_name
}

output "ecs_service_name" {
  description = "GitHub repo variable ECS_SERVICE."
  value       = module.compute.service_name
}

output "backend_task_family" {
  description = "GitHub repo variable ECS_TASK_FAMILY."
  value       = module.compute.backend_task_family
}

output "migrate_task_family" {
  description = "GitHub repo variable ECS_MIGRATE_FAMILY."
  value       = module.compute.migrate_task_family
}

output "ecs_subnet_ids" {
  description = "GitHub repo variable ECS_SUBNETS (private subnets for run-task)."
  value       = module.network.private_subnet_ids
}

output "ecs_security_group_id" {
  description = "GitHub repo variable ECS_SECURITY_GROUP."
  value       = module.network.ecs_sg_id
}

# --- api TLS (Phase 4) ------------------------------------------------------
output "api_certificate_validation_records" {
  description = "CNAMEs to publish at the registrar to validate the api ACM cert."
  value       = module.tls.validation_records
}

output "api_certificate_arn" {
  description = "ISSUED api cert ARN (empty until DNS validation completes)."
  value       = module.tls.certificate_arn
}

# --- SES DNS records (publish in Phase 4) ----------------------------------
output "ses_verification_token" {
  value = module.email.verification_token
}

output "ses_dkim_tokens" {
  value = module.email.dkim_tokens
}

output "ses_mail_from_domain" {
  value = module.email.mail_from_domain
}
