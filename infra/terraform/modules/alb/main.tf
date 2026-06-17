# ALB — public entrypoint for api.<domain>.
#
# Target group is IP-type (Fargate awsvpc) and health-checks /health/ready so
# a task with a broken DB/Redis dependency is pulled from rotation. WebSockets
# (the learning-session layer) traverse the ALB natively — no stickiness
# needed (the WS layer is stateless per the orchestrator design).
#
# TLS: the ACM cert for api.<domain> is requested + DNS-validated in Phase 4.
# Until `certificate_arn` is set, the HTTP:80 listener forwards directly to the
# target group so Phase-3 health checks / smoke tests work over plain HTTP.
# Once the cert exists, HTTP:80 becomes a 301 -> 443 and HTTPS:443 serves.

locals {
  name_prefix  = "lingosai-${var.environment}"
  https_active = var.certificate_arn != ""
}

resource "aws_lb" "this" {
  name               = "${local.name_prefix}-alb"
  load_balancer_type = "application"
  internal           = false
  security_groups    = [var.alb_sg_id]
  subnets            = var.public_subnet_ids

  idle_timeout               = 120 # accommodate streaming WS / long AI calls
  enable_deletion_protection = var.enable_deletion_protection

  tags = { Name = "${local.name_prefix}-alb" }
}

resource "aws_lb_target_group" "backend" {
  name        = "${local.name_prefix}-backend-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  deregistration_delay = 30

  health_check {
    path                = "/health/ready"
    port                = "traffic-port"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    timeout             = 5
    interval            = 15
    matcher             = "200"
  }

  tags = { Name = "${local.name_prefix}-backend-tg" }
}

# HTTP:80 — forwards to the TG pre-TLS; redirects to HTTPS once a cert exists.
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.this.arn
  port              = 80
  protocol          = "HTTP"

  dynamic "default_action" {
    for_each = local.https_active ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }
  dynamic "default_action" {
    for_each = local.https_active ? [] : [1]
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.backend.arn
    }
  }
}

resource "aws_lb_listener" "https" {
  count             = local.https_active ? 1 : 0
  load_balancer_arn = aws_lb.this.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend.arn
  }
}
