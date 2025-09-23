terraform {
  backend "s3" {
    bucket = "terraform-tfstate-backend-sellmystuff"
    key    = "S3/terraform.tfstate"
    region = "eu-central-1"
  }
}
