# DNS records to publish at the registrar in Phase 4. Empty when create=false
# (the env that reuses the shared account identity).

output "verification_token" {
  description = "Add as a TXT record at _amazonses.<domain>."
  value       = one(aws_ses_domain_identity.this[*].verification_token)
}

output "dkim_tokens" {
  description = "Each token T => CNAME <T>._domainkey.<domain> -> <T>.dkim.amazonses.com"
  value       = try(aws_ses_domain_dkim.this[0].dkim_tokens, [])
}

output "mail_from_domain" {
  description = "Publish: MX -> feedback-smtp.<region>.amazonses.com (10) and SPF TXT 'v=spf1 include:amazonses.com ~all'."
  value       = one(aws_ses_domain_mail_from.this[*].mail_from_domain)
}

output "domain_identity_arn" {
  value = one(aws_ses_domain_identity.this[*].arn)
}
