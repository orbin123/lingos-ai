# Remote state in the bootstrap bucket. Run once:
#   terraform init -backend-config=... (or edit the bucket name below to match
#   your bootstrap output) then `terraform init`.
terraform {
  backend "s3" {
    bucket         = "lingosai-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "lingosai-terraform-locks"
    encrypt        = true
  }
}
