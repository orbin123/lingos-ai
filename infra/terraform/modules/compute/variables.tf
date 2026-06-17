variable "environment" {
  type = string
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "ecs_sg_id" {
  type = string
}

variable "target_group_arn" {
  type = string
}

# name -> ARN map (task-def secrets block) and the flat ARN list (execution
# role policy). Both come from the secrets module.
variable "secret_arns" {
  type = map(string)
}

variable "all_secret_arns" {
  type = list(string)
}

variable "environment_variables" {
  description = "Non-secret env injected into the container (ENVIRONMENT, CORS, media, email, model names...)."
  type        = map(string)
}

variable "media_public_bucket_arn" {
  type = string
}

variable "media_private_bucket_arn" {
  type = string
}

variable "image_tag" {
  description = "Initial image tag for the baseline task def. deploy.yml then deploys by git-sha."
  type        = string
  default     = "latest"
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

variable "log_retention_days" {
  type    = number
  default = 30
}
