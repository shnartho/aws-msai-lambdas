data "aws_region" "current" {}

resource "aws_api_gateway_rest_api" "lambda_api" {
  name        = "${var.function_base_name}_api_${var.workspace}"
  description = "API Gateway for ${var.function_base_name} Lambda function"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  binary_media_types = [
    "image/jpeg",
    "image/jpg",
    "image/png"
  ]
}

resource "aws_api_gateway_resource" "lambda_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "images"
}

resource "aws_api_gateway_method" "lambda_method_get" {
  rest_api_id      = aws_api_gateway_rest_api.lambda_api.id
  resource_id      = aws_api_gateway_resource.lambda_resource.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_method" "lambda_method_post" {
  rest_api_id      = aws_api_gateway_rest_api.lambda_api.id
  resource_id      = aws_api_gateway_resource.lambda_resource.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_method" "lambda_method_delete" {
  rest_api_id      = aws_api_gateway_rest_api.lambda_api.id
  resource_id      = aws_api_gateway_resource.lambda_resource.id
  http_method      = "DELETE"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_method" "lambda_method_put" {
  rest_api_id      = aws_api_gateway_rest_api.lambda_api.id
  resource_id      = aws_api_gateway_resource.lambda_resource.id
  http_method      = "PUT"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda_integration_get" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.lambda_resource.id
  http_method             = aws_api_gateway_method.lambda_method_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_integration" "lambda_integration_post" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.lambda_resource.id
  http_method             = aws_api_gateway_method.lambda_method_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_integration" "lambda_integration_delete" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.lambda_resource.id
  http_method             = aws_api_gateway_method.lambda_method_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_integration" "lambda_integration_put" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.lambda_resource.id
  http_method             = aws_api_gateway_method.lambda_method_put.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

resource "aws_api_gateway_deployment" "lambda_deployment" {
  depends_on = [
    aws_api_gateway_method.lambda_method_get,
    aws_api_gateway_method.lambda_method_post,
    aws_api_gateway_method.lambda_method_delete,
    aws_api_gateway_method.lambda_method_put,
    aws_api_gateway_integration.lambda_integration_get,
    aws_api_gateway_integration.lambda_integration_post,
    aws_api_gateway_integration.lambda_integration_delete,
    aws_api_gateway_integration.lambda_integration_put,
  ]

  rest_api_id = aws_api_gateway_rest_api.lambda_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.lambda_resource.id,
      aws_api_gateway_method.lambda_method_get.id,
      aws_api_gateway_method.lambda_method_post.id,
      aws_api_gateway_method.lambda_method_delete.id,
      aws_api_gateway_method.lambda_method_put.id,
      aws_api_gateway_integration.lambda_integration_get.id,
      aws_api_gateway_integration.lambda_integration_post.id,
      aws_api_gateway_integration.lambda_integration_delete.id,
      aws_api_gateway_integration.lambda_integration_put.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "lambda_stage" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  stage_name    = var.workspace
}

resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}

resource "aws_api_gateway_api_key" "client_key" {
  name    = "client-key"
  enabled = true
}

resource "aws_api_gateway_usage_plan" "usage_limit" {
  name = "global-limit"

  api_stages {
    api_id = aws_api_gateway_rest_api.lambda_api.id
    stage  = aws_api_gateway_stage.lambda_stage.stage_name
  }

  throttle_settings {
    rate_limit  = 1
    burst_limit = 1
  }

  quota_settings {
    limit  = 100
    period = "DAY"
  }
}

resource "aws_api_gateway_usage_plan_key" "usage_key_binding" {
  key_id        = aws_api_gateway_api_key.client_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.usage_limit.id
}
