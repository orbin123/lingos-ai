output "alb_dns_name" {
  description = "Point api.<domain> here (CNAME / Route 53 alias) in Phase 4."
  value       = aws_lb.this.dns_name
}

output "alb_zone_id" {
  value = aws_lb.this.zone_id
}

output "alb_arn" {
  value = aws_lb.this.arn
}

output "target_group_arn" {
  value = aws_lb_target_group.backend.arn
}

output "alb_arn_suffix" {
  description = "CloudWatch LoadBalancer dimension."
  value       = aws_lb.this.arn_suffix
}

output "target_group_arn_suffix" {
  description = "CloudWatch TargetGroup dimension."
  value       = aws_lb_target_group.backend.arn_suffix
}
