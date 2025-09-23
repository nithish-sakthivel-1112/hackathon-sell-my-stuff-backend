# IAM policy for Bedrock access
resource "aws_iam_policy" "bedrockaccess" {
  name = "lambdabedrockaccess"
  policy = templatefile(
    "${path.module}/files/iam/lambda_policy.json",
    {
      aws_lambda_arn = aws_lambda_function.sellmystuff.arn
    }
  )
}

resource "aws_iam_role_policy_attachment" "lambdabedrock" {
  role       = aws_iam_role.sellmystufflambdarole.name
  policy_arn = aws_iam_policy.bedrockaccess.arn
}

# IAM policy for CloudWatch Logs access
resource "aws_iam_policy" "cloudwatchaccess" {
  name = "lambdacloudwatchaccess"
  policy = templatefile(
    "${path.module}/files/iam/lambda_policy.json",
    {
      aws_lambda_arn = aws_lambda_function.sellmystuff.arn
    }
  )
}

resource "aws_iam_role_policy_attachment" "lambdacloudwatch" {
  role       = aws_iam_role.sellmystufflambdarole.name
  policy_arn = aws_iam_policy.cloudwatchaccess.arn
}
