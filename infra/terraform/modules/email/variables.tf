variable "domain" {
  description = "Sending domain, e.g. lingosai.com."
  type        = string
}

variable "create" {
  description = "Create the SES identity here. True in exactly one environment (the account-level identity is shared)."
  type        = bool
  default     = false
}
