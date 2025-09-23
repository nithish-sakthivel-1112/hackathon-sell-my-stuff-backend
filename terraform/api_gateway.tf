
resource "aws_api_gateway_rest_api" "sellmystuff" {
  name = "sellmystuff-api"
  body = templatefile("${path.module}/files/api/oas.yml",
    {
      region     = var.aws_region,
      lambda_arn = aws_lambda_function.sellmystuff.arn
    }
  )
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_deployment" "sellmystuff" {
  rest_api_id = aws_api_gateway_rest_api.sellmystuff.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.sellmystuff.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "sellmystuff" {
  deployment_id = aws_api_gateway_deployment.sellmystuff.id
  rest_api_id   = aws_api_gateway_rest_api.sellmystuff.id
  stage_name    = "sellmystuff"
}

resource "aws_api_gateway_usage_plan" "sellmystuff" {
  name = "sellmystuff_usage_plan"

  api_stages {
    api_id = aws_api_gateway_rest_api.sellmystuff.id
    stage  = aws_api_gateway_stage.sellmystuff.stage_name
  }
}

resource "aws_api_gateway_api_key" "sellmystuff" {
  name = "sellmystuff"
}

resource "aws_api_gateway_usage_plan_key" "main" {
  key_id        = aws_api_gateway_api_key.sellmystuff.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.sellmystuff.id
}
