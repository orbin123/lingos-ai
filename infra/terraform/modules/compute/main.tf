# Compute — ECR, ECS Fargate cluster, IAM roles, task definitions, service.
#
# The backend runs as a Fargate service in the private subnets, fronted by the
# ALB target group. A separate migration task definition (same image, command
# overridden to `alembic upgrade head`) is run as a one-off by deploy.yml
# BEFORE the service update, so concurrent tasks never race the same migration.
#
# Two roles:
#   * execution role — pulls the image from ECR, writes logs, reads the
#     secrets the task injects (ECS uses this to resolve the `secrets` block).
#   * task role — what the app itself can do: read/write the media buckets and
#     send via SES.
#
# Image lifecycle: deploy.yml registers new task-def revisions out-of-band, so
# Terraform ignores the live image + task-def revision to avoid fighting CD.

data "aws_region" "current" {}

locals {
  name_prefix = "lingosai-${var.environment}"
  region      = data.aws_region.current.name
  container   = "backend"

  # Secrets block: [{name, valueFrom}] from the name -> ARN map.
  secrets = [for name, arn in var.secret_arns : { name = name, valueFrom = arn }]
  # Non-secret env: [{name, value}] from the plain map.
  environment = [for k, v in var.environment_variables : { name = k, value = v }]
}

# --- ECR --------------------------------------------------------------------

resource "aws_ecr_repository" "backend" {
  # Per-environment repo so staging and production Terraform states never race
  # the same global ECR name. deploy.yml reads the repo URL from a GitHub
  # variable (terraform output), so it adapts to whichever env it targets.
  name                 = "lingosai-backend-${var.environment}"
  image_tag_mutability = "IMMUTABLE" # git-sha tags never change
  force_delete         = false

  image_scanning_configuration {
    scan_on_push = true
  }
  tags = { Name = "lingosai-backend-${var.environment}" }
}

resource "aws_ecr_lifecycle_policy" "backend" {
  repository = aws_ecr_repository.backend.name
  policy = jsonencode({
    rules = [{
      rulePriority = 1
      description  = "Keep the last 20 images"
      selection = {
        tagStatus   = "any"
        countType   = "imageCountMoreThan"
        countNumber = 20
      }
      action = { type = "expire" }
    }]
  })
}

# --- Logs -------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${local.name_prefix}-backend"
  retention_in_days = var.log_retention_days
  tags              = { Name = "${local.name_prefix}-backend-logs" }
}

# --- IAM: execution role ----------------------------------------------------

data "aws_iam_policy_document" "ecs_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "execution" {
  name               = "${local.name_prefix}-ecs-execution"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

resource "aws_iam_role_policy_attachment" "execution_managed" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Let the execution role resolve the secrets injected by the task.
data "aws_iam_policy_document" "execution_secrets" {
  statement {
    actions   = ["secretsmanager:GetSecretValue"]
    resources = var.all_secret_arns
  }
}

resource "aws_iam_role_policy" "execution_secrets" {
  name   = "${local.name_prefix}-execution-secrets"
  role   = aws_iam_role.execution.id
  policy = data.aws_iam_policy_document.execution_secrets.json
}

# --- IAM: task role (what the app can do) -----------------------------------

resource "aws_iam_role" "task" {
  name               = "${local.name_prefix}-ecs-task"
  assume_role_policy = data.aws_iam_policy_document.ecs_assume.json
}

data "aws_iam_policy_document" "task" {
  statement {
    sid     = "MediaReadWrite"
    actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject", "s3:ListBucket"]
    resources = [
      var.media_public_bucket_arn,
      "${var.media_public_bucket_arn}/*",
      var.media_private_bucket_arn,
      "${var.media_private_bucket_arn}/*",
    ]
  }
  statement {
    sid       = "SendEmail"
    actions   = ["ses:SendEmail", "ses:SendRawEmail"]
    resources = ["*"]
  }
  # ECS Exec: SSM Session Manager messaging so an IAM-gated operator can open an
  # interactive shell in a running task (`aws ecs execute-command`). Used for the
  # DR row-verify drill — reads the restore endpoint from inside the VPC using the
  # password already injected as DATABASE_URL, never an env override. Egress to the
  # SSM endpoints rides the existing all-egress ECS SG via NAT (no VPC endpoint).
  statement {
    sid = "ECSExecSSMMessages"
    actions = [
      "ssmmessages:CreateControlChannel",
      "ssmmessages:CreateDataChannel",
      "ssmmessages:OpenControlChannel",
      "ssmmessages:OpenDataChannel",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "task" {
  name   = "${local.name_prefix}-task"
  role   = aws_iam_role.task.id
  policy = data.aws_iam_policy_document.task.json
}

# --- ECS cluster ------------------------------------------------------------

resource "aws_ecs_cluster" "this" {
  name = "${local.name_prefix}"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
  tags = { Name = "${local.name_prefix}-cluster" }
}

# --- Task definitions -------------------------------------------------------

resource "aws_ecs_task_definition" "backend" {
  family                   = "${local.name_prefix}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name        = local.container
    image       = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
    essential   = true
    environment = local.environment
    secrets     = local.secrets
    portMappings = [{
      containerPort = var.app_port
      protocol      = "tcp"
    }]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "backend"
      }
    }
  }])

  # deploy.yml registers new revisions with new image shas — don't let
  # Terraform revert the live image on every apply.
  lifecycle {
    ignore_changes = [container_definitions]
  }
}

resource "aws_ecs_task_definition" "migrate" {
  family                   = "${local.name_prefix}-migrate"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn

  container_definitions = jsonencode([{
    name        = "migrate"
    image       = "${aws_ecr_repository.backend.repository_url}:${var.image_tag}"
    essential   = true
    command     = ["alembic", "upgrade", "head"]
    environment = local.environment
    secrets     = local.secrets
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        "awslogs-group"         = aws_cloudwatch_log_group.backend.name
        "awslogs-region"        = local.region
        "awslogs-stream-prefix" = "migrate"
      }
    }
  }])

  lifecycle {
    ignore_changes = [container_definitions]
  }
}

# --- ECS service ------------------------------------------------------------

resource "aws_ecs_service" "backend" {
  name            = "${local.name_prefix}-backend"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  # ECS Exec: lets an IAM-gated operator open an interactive shell in a running
  # task (DR row-verify drill, §G8 / RUNBOOK §3). Not in `ignore_changes` and
  # deploy.yml only touches `--task-definition`, so neither Terraform nor CD
  # reverts it. Takes effect only for tasks launched AFTER the change — the
  # founder must `--force-new-deployment` once (see G8 runbook).
  enable_execute_command = true

  # Zero-downtime rolling deploy: never drop below 100% healthy, allow 200%
  # during a rollout so new tasks come up before old ones drain.
  deployment_minimum_healthy_percent = 100
  deployment_maximum_percent         = 200

  network_configuration {
    subnets          = var.private_subnet_ids
    security_groups  = [var.ecs_sg_id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = var.target_group_arn
    container_name   = local.container
    container_port   = var.app_port
  }

  # The target group must be attached to a listener before the service can
  # register targets — the env wires `depends_on = [module.alb]` on this
  # module to guarantee that ordering.

  # deploy.yml updates the running task definition out-of-band.
  lifecycle {
    ignore_changes = [task_definition, desired_count]
  }
}
