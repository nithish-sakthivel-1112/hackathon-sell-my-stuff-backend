variable "aws_region" {
  description = "The AWS region to deploy resources in"
  type        = string
  default     = "eu-central-1"
}

variable "python_version" {
  description = "The Python version to use for the Lambda function"
  type        = string
  default     = "python3.13"
}

variable "artifact_bucket_name" {
  description = "The name of the S3 bucket to store Lambda deployment packages"
  type        = string
  default     = "app-artifacts-nithish"
}

variable "lambda_function_pack" {
  description = "The name of the Lambda deployment package zip file"
  type        = string
  default     = "lambda_package.zip"
}

variable "dependency_file" {
  description = "The name of the file containingdependencies"
  type        = string
  default     = "dependencies.zip"
}
