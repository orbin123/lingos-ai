variable "environment" {
  description = "Environment name (staging | production)."
  type        = string
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "app_port" {
  description = "Container port the backend listens on."
  type        = number
  default     = 8000
}
