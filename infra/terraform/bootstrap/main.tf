# Bootstrap — the remote-state backend itself.
#
# Chicken-and-egg: the rest of the Terraform stores its state in S3 with a
# DynamoDB lock, but those have to exist first. This tiny root creates them
# with LOCAL state (committed nowhere — it only describes two resources you
# never destroy). Run it ONCE per AWS account, before any env apply.
#
#   terraform -chdir=infra/terraform/bootstrap init
#   terraform -chdir=infra/terraform/bootstrap apply
#
# After this, envs/* use the S3 backend created here. See docs/AWS_SETUP.md.

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.70"
    }
  }
}

provider "aws" {
  region = var.region
  default_tags {
    tags = {
      Project   = "lingosai"
      ManagedBy = "terraform"
      Component = "tf-state-bootstrap"
    }
  }
}

# Versioned bucket holding every workspace's state file. Versioning means a
# bad apply that corrupts state can be rolled back to a prior object version.
resource "aws_s3_bucket" "state" {
  bucket = var.state_bucket_name

  # State is irreplaceable operational data — never let `terraform destroy`
  # (or a fat-fingered apply) remove the bucket.
  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_s3_bucket_versioning" "state" {
  bucket = aws_s3_bucket.state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "state" {
  bucket = aws_s3_bucket.state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "state" {
  bucket                  = aws_s3_bucket.state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Lock table so two concurrent applies can't race the same state.
resource "aws_dynamodb_table" "lock" {
  name         = var.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  lifecycle {
    prevent_destroy = true
  }
}
