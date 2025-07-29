output "function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.lambda.function_name
}

output "invoke_arn" {
  description = "The ARN to be used for invoking the Lambda function via API Gateway"
  value       = aws_lambda_function.lambda.invoke_arn
}
