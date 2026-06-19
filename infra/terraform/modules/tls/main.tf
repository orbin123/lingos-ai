# TLS — ACM certificate for api.<domain>, DNS-validated.
#
# DNS authority is Namecheap (not Route 53, per AD-7), so the validation records
# cannot be created by Terraform. The cert is therefore brought up in two steps:
#
#   1. terraform apply -target='...module.tls.aws_acm_certificate.api[0]'
#        → creates the cert (status PENDING_VALIDATION).
#   2. publish the `validation_records` output as CNAMEs at Namecheap, plus the
#      `api` CNAME -> the ALB DNS name.
#   3. terraform apply
#        → aws_acm_certificate_validation polls ACM until the cert is ISSUED,
#          then `certificate_arn` flows to the ALB and the HTTPS:443 listener +
#          HTTP->443 redirect appear (see modules/alb).
#
# `certificate_arn` is sourced from the *validation* resource, not the cert, so
# the ALB only ever attaches a cert that ACM has actually ISSUED — a half-applied
# state can never wire an un-issued cert onto the listener.

resource "aws_acm_certificate" "api" {
  count             = var.create ? 1 : 0
  domain_name       = var.api_domain
  validation_method = "DNS"

  # Replace-then-swap if the domain ever changes, so the ALB never references a
  # cert mid-destroy.
  lifecycle {
    create_before_destroy = true
  }

  tags = { Name = var.api_domain }
}

# Waits for the cert to reach ISSUED. No `validation_record_fqdns` is given
# because the CNAMEs are published by hand at Namecheap — ACM issues the cert
# once they propagate and this resource simply blocks until then.
resource "aws_acm_certificate_validation" "api" {
  count           = var.create ? 1 : 0
  certificate_arn = aws_acm_certificate.api[0].arn

  timeouts {
    create = "60m"
  }
}
