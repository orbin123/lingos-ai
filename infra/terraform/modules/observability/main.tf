# Observability — SNS alert topic + the few high-signal alarms that mean
# "act now" (plan §5.1). Everything else lives on dashboards, not pages, to
# avoid alert fatigue. One on-call: the founder, reached by email via SNS.

locals {
  name_prefix = "lingosai-${var.environment}"
}

resource "aws_sns_topic" "alerts" {
  name = "${local.name_prefix}-alerts"
  tags = { Name = "${local.name_prefix}-alerts" }
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email == "" ? 0 : 1
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# --- ALB: user-facing symptoms ---------------------------------------------

resource "aws_cloudwatch_metric_alarm" "alb_5xx" {
  alarm_name          = "${local.name_prefix}-alb-5xx"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Backend is returning 5xx — likely an app or dependency failure."
  treat_missing_data  = "notBreaching"
  dimensions          = { LoadBalancer = var.alb_arn_suffix }
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy" {
  alarm_name          = "${local.name_prefix}-alb-unhealthy-hosts"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "UnHealthyHostCount"
  namespace           = "AWS/ApplicationELB"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "An ECS target is failing /health/ready."
  treat_missing_data  = "notBreaching"
  dimensions = {
    LoadBalancer = var.alb_arn_suffix
    TargetGroup  = var.target_group_arn_suffix
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# --- ECS: capacity ----------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "ecs_cpu" {
  alarm_name          = "${local.name_prefix}-ecs-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Backend service CPU sustained high — consider scaling task count."
  treat_missing_data  = "notBreaching"
  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = var.service_name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory" {
  alarm_name          = "${local.name_prefix}-ecs-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "MemoryUtilization"
  namespace           = "AWS/ECS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Backend service memory sustained high — risk of OOM task kills."
  treat_missing_data  = "notBreaching"
  dimensions = {
    ClusterName = var.cluster_name
    ServiceName = var.service_name
  }
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# --- RDS --------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "rds_cpu" {
  alarm_name          = "${local.name_prefix}-rds-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "RDS CPU sustained high — risk of credit exhaustion on t-class."
  treat_missing_data  = "notBreaching"
  dimensions          = { DBInstanceIdentifier = var.db_instance_id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_storage" {
  alarm_name          = "${local.name_prefix}-rds-free-storage-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 2147483648 # 2 GiB
  alarm_description   = "RDS free storage below 2 GiB."
  treat_missing_data  = "notBreaching"
  dimensions          = { DBInstanceIdentifier = var.db_instance_id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_cpu_credits" {
  alarm_name          = "${local.name_prefix}-rds-cpu-credits-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUCreditBalance"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 50
  alarm_description   = "RDS t-class CPU credit balance low — sustained CPU will start to throttle."
  treat_missing_data  = "notBreaching"
  dimensions          = { DBInstanceIdentifier = var.db_instance_id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "rds_connections" {
  alarm_name          = "${local.name_prefix}-rds-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 60
  statistic           = "Average"
  threshold           = var.rds_connections_alarm_threshold
  alarm_description   = "RDS connection count high — possible leak; consider pooling (RDS Proxy/PgBouncer)."
  treat_missing_data  = "notBreaching"
  dimensions          = { DBInstanceIdentifier = var.db_instance_id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# --- Cost: AWS Budgets (plan §5.7) -----------------------------------------
# Spend guardrail so cost never surprises the founder. Notifies alert_email
# directly (Budgets emails its own subscribers — no SNS topic policy needed).
# Tracks total AWS spend; OpenAI/other non-AWS cost is watched on the AI-cost
# dashboard, not here.

locals {
  budget_notifications = var.alert_email == "" ? [] : [
    { type = "ACTUAL", threshold = 80 },      # 80% of budget already spent
    { type = "FORECASTED", threshold = 100 }, # on track to exceed 100%
  ]
}

resource "aws_budgets_budget" "monthly_cost" {
  name         = "${local.name_prefix}-monthly-cost"
  budget_type  = "COST"
  limit_amount = format("%d", var.monthly_budget_usd)
  limit_unit   = "USD"
  time_unit    = "MONTHLY"

  dynamic "notification" {
    for_each = local.budget_notifications
    content {
      comparison_operator        = "GREATER_THAN"
      threshold                  = notification.value.threshold
      threshold_type             = "PERCENTAGE"
      notification_type          = notification.value.type
      subscriber_email_addresses = [var.alert_email]
    }
  }
}

# --- Redis ------------------------------------------------------------------

resource "aws_cloudwatch_metric_alarm" "redis_memory" {
  alarm_name          = "${local.name_prefix}-redis-memory-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "DatabaseMemoryUsagePercentage"
  namespace           = "AWS/ElastiCache"
  period              = 60
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Redis memory high — rate-limit/lock keys may evict."
  treat_missing_data  = "notBreaching"
  dimensions          = { CacheClusterId = "${var.redis_replication_group_id}-001" }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "redis_evictions" {
  alarm_name          = "${local.name_prefix}-redis-evictions"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Evictions"
  namespace           = "AWS/ElastiCache"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Redis is evicting keys — memory pressure; rate-limit/lock keys may be lost."
  treat_missing_data  = "notBreaching"
  dimensions          = { CacheClusterId = "${var.redis_replication_group_id}-001" }
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

# --- Synthetic uptime check (plan 5.1) -------------------------------------
# Route53 global health check hits the endpoint from multiple AWS regions every
# 30s; the alarm pages via SNS before users notice. HealthCheckStatus metrics
# are published in us-east-1 (where this stack runs). Uses /health (liveness),
# not /health/ready, so a transient dependency blip the ALB already handles
# doesn't page.

resource "aws_route53_health_check" "uptime" {
  count             = var.uptime_check_fqdn == "" ? 0 : 1
  fqdn              = var.uptime_check_fqdn
  type              = "HTTPS"
  port              = 443
  resource_path     = "/health"
  request_interval  = 30
  failure_threshold = 3
  tags              = { Name = "${local.name_prefix}-uptime" }
}

resource "aws_cloudwatch_metric_alarm" "uptime" {
  count               = var.uptime_check_fqdn == "" ? 0 : 1
  alarm_name          = "${local.name_prefix}-uptime-health"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "HealthCheckStatus"
  namespace           = "AWS/Route53"
  period              = 60
  statistic           = "Minimum"
  threshold           = 1
  alarm_description   = "Synthetic check: ${var.uptime_check_fqdn}/health is failing from multiple regions."
  treat_missing_data  = "breaching"
  dimensions          = { HealthCheckId = aws_route53_health_check.uptime[0].id }
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}
