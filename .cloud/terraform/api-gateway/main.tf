# Get current AWS region
data "aws_region" "current" {}

# Create API Gateway REST API
resource "aws_api_gateway_rest_api" "lambda_api" {
  name        = "${var.function_base_name}_api_${var.workspace}"
  description = "API Gateway for ${var.function_base_name} Lambda function"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }
}

# Create API Gateway resource (endpoint path)
resource "aws_api_gateway_resource" "lambda_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "hello"
}

# Create API Gateway method (GET)
resource "aws_api_gateway_method" "lambda_method_get" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.lambda_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# Create API Gateway method (POST)
resource "aws_api_gateway_method" "lambda_method_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.lambda_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Create API Gateway method (DELETE)
resource "aws_api_gateway_method" "lambda_method_delete" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.lambda_resource.id
  http_method   = "DELETE"
  authorization = "NONE"
}

# Create API Gateway integration with Lambda (GET)
resource "aws_api_gateway_integration" "lambda_integration_get" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.lambda_resource.id
  http_method = aws_api_gateway_method.lambda_method_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Create API Gateway integration with Lambda (POST)
resource "aws_api_gateway_integration" "lambda_integration_post" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.lambda_resource.id
  http_method = aws_api_gateway_method.lambda_method_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Create API Gateway integration with Lambda (DELETE)
resource "aws_api_gateway_integration" "lambda_integration_delete" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.lambda_resource.id
  http_method = aws_api_gateway_method.lambda_method_delete.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Create API Gateway deployment
resource "aws_api_gateway_deployment" "lambda_deployment" {
  depends_on = [
    aws_api_gateway_method.lambda_method_get,
    aws_api_gateway_method.lambda_method_post,
    aws_api_gateway_method.lambda_method_delete,
    aws_api_gateway_integration.lambda_integration_get,
    aws_api_gateway_integration.lambda_integration_post,
    aws_api_gateway_integration.lambda_integration_delete,
  ]

  rest_api_id = aws_api_gateway_rest_api.lambda_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.lambda_resource.id,
      aws_api_gateway_method.lambda_method_get.id,
      aws_api_gateway_method.lambda_method_post.id,
      aws_api_gateway_method.lambda_method_delete.id,
      aws_api_gateway_integration.lambda_integration_get.id,
      aws_api_gateway_integration.lambda_integration_post.id,
      aws_api_gateway_integration.lambda_integration_delete.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Create API Gateway stage
resource "aws_api_gateway_stage" "lambda_stage" {
  deployment_id = aws_api_gateway_deployment.lambda_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  stage_name    = var.workspace
}

# Give API Gateway permission to invoke Lambda
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}