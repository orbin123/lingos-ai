output "state_bucket" {
  description = "Use this as the S3 backend bucket in envs/*/backend.tf."
  value       = aws_s3_bucket.state.id
}

output "lock_table" {
  description = "Use this as the S3 backend dynamodb_table in envs/*/backend.tf."
  value       = aws_dynamodb_table.lock.name
}
