data "aws_region" "current" {}

resource "aws_api_gateway_rest_api" "lambda_api" {
  name        = "${var.function_name}_api_${var.workspace}"
  description = "API Gateway for ${var.function_name} Lambda function"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

resource "aws_api_gateway_resource" "lambda_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "auth"
}

# /auth/login resource
resource "aws_api_gateway_resource" "login_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.lambda_resource.id
  path_part   = "login"
}

# /auth/signup resource
resource "aws_api_gateway_resource" "signup_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.lambda_resource.id
  path_part   = "signup"
}

# POST method for /auth/login
resource "aws_api_gateway_method" "login_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.login_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# POST method for /auth/signup
resource "aws_api_gateway_method" "signup_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.signup_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Lambda integration for /auth/login POST
resource "aws_api_gateway_integration" "login_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.login_resource.id
  http_method = aws_api_gateway_method.login_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambda_invoke_arn
}

# Lambda integration for /auth/signup POST
resource "aws_api_gateway_integration" "signup_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.signup_resource.id
  http_method = aws_api_gateway_method.signup_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambda_invoke_arn
}

# Lambda permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw_auth_invoke" {
  statement_id  = "AllowAPIGatewayInvokeAuth"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "lambda_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.login_post_integration,
    aws_api_gateway_integration.signup_post_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  stage_name  = var.workspace
}

# API Gateway stage (optional, for more control)
resource "aws_api_gateway_stage" "lambda_api_stage" {
  stage_name    = var.workspace
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  deployment_id = aws_api_gateway_deployment.lambda_api_deployment.id
}

