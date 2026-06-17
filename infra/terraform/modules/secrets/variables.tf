variable "environment" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "rds_address" {
  type = string
}

variable "rds_port" {
  type = number
}

variable "db_name" {
  type = string
}

variable "redis_address" {
  type = string
}

variable "redis_port" {
  type = number
}
