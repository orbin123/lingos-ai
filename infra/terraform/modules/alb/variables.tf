variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "alb_sg_id" {
  type = string
}

variable "app_port" {
  type    = number
  default = 8000
}

variable "certificate_arn" {
  description = "ACM cert ARN for api.<domain>. May be known-after-apply when TF manages the cert."
  type        = string
  default     = ""
}

# A *static* on/off for HTTPS — must not depend on a resource attribute, so the
# listener `count` is always determinable at plan time even while certificate_arn
# is still known-after-apply (TF-managed cert).
variable "enable_https" {
  description = "Serve HTTPS:443 (cert) + redirect HTTP:80->443. False = HTTP-only (Phase 3)."
  type        = bool
  default     = false
}

variable "enable_deletion_protection" {
  type    = bool
  default = false
}
