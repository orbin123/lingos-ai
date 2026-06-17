# Media — S3 + CloudFront.
#
# Two buckets:
#   * public  — TTS audio, images, blog covers. Private at the S3 level but
#     fronted by CloudFront via Origin Access Control (OAC); the browser only
#     ever reaches it through the CDN.
#   * private — learner audio recordings. NO CloudFront, no public access; the
#     app streams bytes through an owner-checked route (S3BlobStorage private
#     mode). This is why it is a distinct bucket: nothing learner-owned is
#     reachable via the CDN even with a guessed key.
#
# Both have versioning + a lifecycle rule (plan §3.9).

locals {
  name_prefix = "lingosai-${var.environment}"
}

# --- Public media bucket ----------------------------------------------------

resource "aws_s3_bucket" "public" {
  bucket = "${local.name_prefix}-media"
  tags   = { Name = "${local.name_prefix}-media" }
}

resource "aws_s3_bucket_versioning" "public" {
  bucket = aws_s3_bucket.public.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "public" {
  bucket                  = aws_s3_bucket.public.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "public" {
  bucket = aws_s3_bucket.public.id
  rule {
    id     = "expire-old-noncurrent"
    status = "Enabled"
    filter {}
    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# --- Private learner-audio bucket -------------------------------------------

resource "aws_s3_bucket" "private" {
  bucket = "${local.name_prefix}-media-private"
  tags   = { Name = "${local.name_prefix}-media-private" }
}

resource "aws_s3_bucket_versioning" "private" {
  bucket = aws_s3_bucket.private.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "private" {
  bucket                  = aws_s3_bucket.private.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "private" {
  bucket = aws_s3_bucket.private.id
  rule {
    id     = "expire-learner-audio"
    status = "Enabled"
    filter {}
    expiration {
      days = 90 # learner clips are graded on submit; no need to keep forever
    }
    noncurrent_version_expiration {
      noncurrent_days = 7
    }
  }
}

# --- CloudFront in front of the public bucket -------------------------------

resource "aws_cloudfront_origin_access_control" "public" {
  name                              = "${local.name_prefix}-media-oac"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "public" {
  enabled         = true
  comment         = "${local.name_prefix} media CDN"
  is_ipv6_enabled = true
  price_class     = "PriceClass_100" # NA + EU; cheapest tier

  origin {
    domain_name              = aws_s3_bucket.public.bucket_regional_domain_name
    origin_id                = "s3-public-media"
    origin_access_control_id = aws_cloudfront_origin_access_control.public.id
  }

  default_cache_behavior {
    target_origin_id       = "s3-public-media"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    compress               = true
    # AWS managed "CachingOptimized" policy — content is hash-addressed and
    # immutable, so long TTLs are safe and cut origin fetches.
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
  }

  # Optional custom domain (e.g. media.lingosai.com), wired in Phase 4.
  dynamic "viewer_certificate" {
    for_each = var.cdn_acm_certificate_arn == "" ? [] : [1]
    content {
      acm_certificate_arn      = var.cdn_acm_certificate_arn
      ssl_support_method       = "sni-only"
      minimum_protocol_version = "TLSv1.2_2021"
    }
  }
  dynamic "viewer_certificate" {
    for_each = var.cdn_acm_certificate_arn == "" ? [1] : []
    content {
      cloudfront_default_certificate = true
    }
  }

  aliases = var.cdn_domain_aliases

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  tags = { Name = "${local.name_prefix}-media-cdn" }
}

# Allow only this CloudFront distribution to read the public bucket.
data "aws_iam_policy_document" "public_bucket" {
  statement {
    sid     = "AllowCloudFrontRead"
    actions = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.public.arn}/*"]
    principals {
      type        = "Service"
      identifiers = ["cloudfront.amazonaws.com"]
    }
    condition {
      test     = "StringEquals"
      variable = "AWS:SourceArn"
      values   = [aws_cloudfront_distribution.public.arn]
    }
  }
}

resource "aws_s3_bucket_policy" "public" {
  bucket = aws_s3_bucket.public.id
  policy = data.aws_iam_policy_document.public_bucket.json
}
