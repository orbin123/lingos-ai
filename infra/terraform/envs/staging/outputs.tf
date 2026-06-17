output "alb_dns_name" { value = module.stack.alb_dns_name }
output "alb_zone_id" { value = module.stack.alb_zone_id }
output "cdn_domain_name" { value = module.stack.cdn_domain_name }
output "media_public_bucket" { value = module.stack.media_public_bucket }
output "media_private_bucket" { value = module.stack.media_private_bucket }

output "github_deploy_role_arn" { value = module.stack.github_deploy_role_arn }
output "ecr_repository_url" { value = module.stack.ecr_repository_url }
output "ecs_cluster_name" { value = module.stack.ecs_cluster_name }
output "ecs_service_name" { value = module.stack.ecs_service_name }
output "backend_task_family" { value = module.stack.backend_task_family }
output "migrate_task_family" { value = module.stack.migrate_task_family }
output "ecs_subnet_ids" { value = module.stack.ecs_subnet_ids }
output "ecs_security_group_id" { value = module.stack.ecs_security_group_id }

output "ses_verification_token" { value = module.stack.ses_verification_token }
output "ses_dkim_tokens" { value = module.stack.ses_dkim_tokens }
output "ses_mail_from_domain" { value = module.stack.ses_mail_from_domain }
