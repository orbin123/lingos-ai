output "public_bucket" {
  description = "MEDIA_S3_BUCKET"
  value       = aws_s3_bucket.public.id
}

output "public_bucket_arn" {
  value = aws_s3_bucket.public.arn
}

output "private_bucket" {
  description = "MEDIA_PRIVATE_S3_BUCKET"
  value       = aws_s3_bucket.private.id
}

output "private_bucket_arn" {
  value = aws_s3_bucket.private.arn
}

output "cdn_domain_name" {
  description = "CloudFront domain — base for MEDIA_CDN_URL (prepend https://)."
  value       = aws_cloudfront_distribution.public.domain_name
}

output "cdn_distribution_id" {
  value = aws_cloudfront_distribution.public.id
}
