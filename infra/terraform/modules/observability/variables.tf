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

variable "uptime_check_fqdn" {
  description = "FQDN for the Route53 synthetic /health check. Empty = no uptime check."
  type        = string
  default     = ""
}

variable "rds_connections_alarm_threshold" {
  description = "Alarm when average RDS connections exceed this (tune to instance class max_connections)."
  type        = number
  default     = 100
}

variable "nat_gateway_id" {
  description = "NAT gateway id for the egress error alarm. Empty = no alarm."
  type        = string
  default     = ""
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
