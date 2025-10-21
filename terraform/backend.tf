terraform {
  backend "s3" {
    bucket = "terraform-tfstate-backend-1"
    key    = "S3/terraform.tfstate"
    region = "eu-central-1"
  }
}
