terraform {
  backend "s3" {
    bucket         = "lingosai-terraform-state"
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "lingosai-terraform-locks"
    encrypt        = true
  }
}
