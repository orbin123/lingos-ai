variable "environment" {
  type = string
}

variable "alert_email" {
  description = "Email subscribed to the SNS alert topic. Empty = topic only."
  type        = string
  default     = ""
}

variable "monthly_budget_usd" {
  description = "Monthly AWS cost budget (USD). Alerts at 80% actual + 100% forecasted to alert_email."
  type        = number
  default     = 200
}

variable "alb_arn_suffix" {
  type = string
}

variable "target_group_arn_suffix" {
  type = string
}

variable "cluster_name" {
  type = string
}

variable "service_name" {
  type = string
}

variable "db_instance_id" {
  type = string
}

variable "redis_replication_group_id" {
  type = string
}
