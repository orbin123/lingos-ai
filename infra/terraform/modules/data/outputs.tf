# Plain postgresql:// — database.py rewrites it to postgresql+psycopg:// at
# runtime. The founder assembles the full DATABASE_URL secret from these.
output "rds_address" {
  value = aws_db_instance.this.address
}

output "rds_port" {
  value = aws_db_instance.this.port
}

output "db_name" {
  value = aws_db_instance.this.db_name
}

# Redis has transit encryption on, so the app must connect with rediss:// .
output "redis_primary_endpoint" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}

output "redis_port" {
  value = aws_elasticache_replication_group.this.port
}

output "db_instance_id" {
  description = "CloudWatch DBInstanceIdentifier dimension."
  value       = aws_db_instance.this.identifier
}

output "redis_replication_group_id" {
  value = aws_elasticache_replication_group.this.replication_group_id
}
