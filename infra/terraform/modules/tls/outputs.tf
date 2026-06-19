# Publish each record as a CNAME at the registrar to validate the cert. ACM
# de-duplicates identical records, so a single-domain cert yields one entry.
output "validation_records" {
  description = "CNAMEs to publish at Namecheap to validate the api ACM cert."
  value = var.create ? [
    for o in aws_acm_certificate.api[0].domain_validation_options : {
      name  = o.resource_record_name
      type  = o.resource_record_type
      value = o.resource_record_value
    }
  ] : []
}

# Empty until validation completes; feeds modules/alb's certificate_arn, which
# keys HTTPS-on-or-off off a non-empty value.
output "certificate_arn" {
  description = "ISSUED api cert ARN (empty until DNS validation completes)."
  value       = var.create ? one(aws_acm_certificate_validation.api[*].certificate_arn) : ""
}
