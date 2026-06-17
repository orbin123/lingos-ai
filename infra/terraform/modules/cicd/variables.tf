variable "environment" {
  type = string
}

variable "github_repo" {
  description = "owner/repo that may assume the deploy role, e.g. orbin123/lingos-ai."
  type        = string
}

variable "create_oidc_provider" {
  description = "Create the account-global GitHub OIDC provider here. True in exactly one environment."
  type        = bool
  default     = false
}

variable "ecr_repository_arn" {
  type = string
}

variable "passable_role_arns" {
  description = "Task + execution role ARNs deploy.yml may PassRole to ECS."
  type        = list(string)
}
