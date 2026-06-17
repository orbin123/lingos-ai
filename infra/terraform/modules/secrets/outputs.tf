# name -> secret ARN, consumed by the ECS task definition `secrets` block.
# The ARNs (without a version/stage suffix) resolve to AWSCURRENT.
output "secret_arns" {
  value = merge(
    {
      DATABASE_URL = aws_secretsmanager_secret.database_url.arn
      REDIS_URL    = aws_secretsmanager_secret.redis_url.arn
    },
    { for name, s in aws_secretsmanager_secret.app : name => s.arn },
  )
}

# Flat list for the execution role's secretsmanager:GetSecretValue policy.
output "all_secret_arns" {
  value = concat(
    [
      aws_secretsmanager_secret.database_url.arn,
      aws_secretsmanager_secret.redis_url.arn,
    ],
    [for s in aws_secretsmanager_secret.app : s.arn],
  )
}
