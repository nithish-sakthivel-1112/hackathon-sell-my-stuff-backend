data "aws_s3_object" "lambda_package" {
  bucket = var.artifact_bucket_name
  key    = var.lambda_function_pack
}

data "aws_s3_object" "dependencies" {
  bucket = var.artifact_bucket_name
  key    = var.dependency_file
}

# Permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "api_gateway_sellmystuff" {
  statement_id  = "AllowSellMyStuffAPIInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "sellmystuff_lambda"
  principal     = "apigateway.amazonaws.com"

  # The /* part allows invocation from any stage, method and resource path
  # within API Gateway.
  source_arn = "${aws_api_gateway_rest_api.sellmystuff.execution_arn}/*"
}


resource "aws_iam_role" "sellmystufflambdarole" {
  name = "sellmystufflambdarole"
  assume_role_policy = templatefile("${path.module}/files/iam/assume_role.json", {
    service = "lambda.amazonaws.com"
  })
}

resource "aws_lambda_layer_version" "sellmystuff_dependencies" {
  s3_bucket         = data.aws_s3_object.dependencies.bucket
  s3_key            = data.aws_s3_object.dependencies.key
  s3_object_version = data.aws_s3_object.dependencies.version_id
  layer_name        = "sellmystuff_dependencies"
  description       = "Common dependencies for sellmystuff Lambda functions"

  compatible_runtimes      = [var.python_version]
  compatible_architectures = ["x86_64", "arm64"]
}


resource "aws_lambda_function" "sellmystuff" {
  function_name     = "sell-my-stuff"
  handler           = "sell_my_stuff.lambda_handler.lambda_handler"
  runtime           = var.python_version
  role              = aws_iam_role.sellmystufflambdarole.arn
  s3_bucket         = data.aws_s3_object.lambda_package.bucket
  s3_key            = data.aws_s3_object.lambda_package.key
  s3_object_version = data.aws_s3_object.lambda_package.version_id
  layers            = [aws_lambda_layer_version.sellmystuff_dependencies.arn]
  timeout           = 300
}


