provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = "Development"
      Project     = "sell-my-stuff-hackatthon"
    }
  }
}
