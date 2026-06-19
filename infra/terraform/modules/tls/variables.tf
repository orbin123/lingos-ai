variable "create" {
  description = "Request the api ACM certificate in this env (true in exactly one — the env that owns api.<domain>)."
  type        = bool
  default     = false
}

variable "api_domain" {
  description = "FQDN the ALB serves and the cert is requested for, e.g. api.lingosai.com."
  type        = string
  default     = ""
}
