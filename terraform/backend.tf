terraform {
  backend "s3" {
    bucket = "terraform-tfstate-backend-1"
    key    = "S3/terraform.tfstate"
    region = "us-east-1"
  }
}
