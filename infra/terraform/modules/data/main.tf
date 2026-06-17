# Data tier — RDS PostgreSQL + ElastiCache Redis, private subnets only.
#
# Both are reachable only from the ECS security group (enforced by the SGs in
# the network module). Multi-AZ is on for production and off for staging to
# save cost. The app's database.py rewrites postgresql:// -> postgresql+psycopg://
# at runtime, so the DATABASE_URL secret stores the plain postgresql:// form.

locals {
  name_prefix = "lingosai-${var.environment}"
}

# --- RDS PostgreSQL ---------------------------------------------------------

resource "aws_db_subnet_group" "this" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = var.private_subnet_ids
  tags       = { Name = "${local.name_prefix}-db-subnets" }
}

resource "aws_db_instance" "this" {
  identifier     = "${local.name_prefix}-postgres"
  engine         = "postgres"
  engine_version = var.postgres_version
  instance_class = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage # storage autoscaling
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password # supplied from the DB_MASTER_PASSWORD secret

  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [var.rds_sg_id]
  multi_az               = var.multi_az
  publicly_accessible    = false

  backup_retention_period = var.backup_retention_days # 7-day PITR
  backup_window           = "03:00-04:00"
  maintenance_window      = "Mon:04:30-Mon:05:30"
  copy_tags_to_snapshot   = true

  deletion_protection       = var.deletion_protection
  skip_final_snapshot       = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${local.name_prefix}-final"

  performance_insights_enabled = true
  auto_minor_version_upgrade   = true

  tags = { Name = "${local.name_prefix}-postgres" }
}

# --- ElastiCache Redis ------------------------------------------------------

resource "aws_elasticache_subnet_group" "this" {
  name       = "${local.name_prefix}-redis-subnets"
  subnet_ids = var.private_subnet_ids
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id = "${local.name_prefix}-redis"
  description          = "LingosAI ${var.environment} Redis (rate limits + locks)"
  engine               = "redis"
  engine_version       = var.redis_version
  node_type            = var.redis_node_type
  port                 = 6379

  # Multi-AZ + a replica for production; single node for staging.
  num_cache_clusters         = var.multi_az ? 2 : 1
  automatic_failover_enabled = var.multi_az
  multi_az_enabled           = var.multi_az

  subnet_group_name  = aws_elasticache_subnet_group.this.name
  security_group_ids = [var.redis_sg_id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  snapshot_retention_limit = var.multi_az ? 5 : 0
  maintenance_window       = "mon:05:30-mon:06:30"

  tags = { Name = "${local.name_prefix}-redis" }
}
