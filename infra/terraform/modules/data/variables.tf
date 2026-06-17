variable "environment" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "rds_sg_id" {
  type = string
}

variable "redis_sg_id" {
  type = string
}

# --- RDS --------------------------------------------------------------------
variable "postgres_version" {
  description = "Match the major version you develop against."
  type        = string
  default     = "16.4"
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.small"
}

variable "db_allocated_storage" {
  type    = number
  default = 20
}

variable "db_max_allocated_storage" {
  type    = number
  default = 100
}

variable "db_name" {
  type    = string
  default = "lingosai"
}

variable "db_username" {
  type    = string
  default = "lingosai"
}

variable "db_password" {
  description = "Master password (from the DB_MASTER_PASSWORD secret)."
  type        = string
  sensitive   = true
}

variable "multi_az" {
  description = "Multi-AZ for prod; single-AZ for staging."
  type        = bool
  default     = false
}

variable "backup_retention_days" {
  type    = number
  default = 7
}

variable "deletion_protection" {
  type    = bool
  default = true
}

variable "skip_final_snapshot" {
  type    = bool
  default = false
}

# --- Redis ------------------------------------------------------------------
variable "redis_version" {
  type    = string
  default = "7.1"
}

variable "redis_node_type" {
  type    = string
  default = "cache.t4g.micro"
}
