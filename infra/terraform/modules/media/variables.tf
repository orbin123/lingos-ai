variable "environment" {
  type = string
}

variable "cdn_acm_certificate_arn" {
  description = "ACM cert ARN (us-east-1) for a custom CDN domain. Empty = use the default *.cloudfront.net cert. Set in Phase 4."
  type        = string
  default     = ""
}

variable "cdn_domain_aliases" {
  description = "Custom CNAMEs for the CDN, e.g. [\"media.lingosai.com\"]. Empty until Phase 4."
  type        = list(string)
  default     = []
}
