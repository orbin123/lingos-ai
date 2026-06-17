# Email — SES domain identity + DKIM.
#
# SES identities are account+region scoped, so the lingosai.com identity is
# created in exactly ONE environment (production, via create=true). Staging
# reuses the same verified account identity — once the domain is verified the
# account can send from noreply@lingosai.com regardless of which env's task
# does the sending. When create=false this module is a no-op.
#
# The DNS records that prove ownership / enable DKIM are emitted as outputs and
# published at the registrar in Phase 4. SES production-access (sandbox exit)
# is an account-level console request the founder files — see docs/AWS_SETUP.md.

resource "aws_ses_domain_identity" "this" {
  count  = var.create ? 1 : 0
  domain = var.domain
}

resource "aws_ses_domain_dkim" "this" {
  count  = var.create ? 1 : 0
  domain = aws_ses_domain_identity.this[0].domain
}

resource "aws_ses_domain_mail_from" "this" {
  count            = var.create ? 1 : 0
  domain           = aws_ses_domain_identity.this[0].domain
  mail_from_domain = "mail.${var.domain}"
}
