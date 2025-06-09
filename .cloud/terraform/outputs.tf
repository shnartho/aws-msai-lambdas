output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda.function_arn
}

output "lambda_function_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  value       = module.lambda.invoke_arn
}

output "workspace" {
  description = "Current workspace"
  value       = var.workspace
}

output "api_gateway_url" {
  description = "URL of the API Gateway endpoint"
  value       = module.api_gateway.api_gateway_url
}

output "api_gateway_base_url" {
  description = "Base URL of the API Gateway"
  value       = module.api_gateway.api_gateway_base_url
}