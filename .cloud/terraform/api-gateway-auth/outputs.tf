output "api_gateway_id" {
  description = "The ID of the API Gateway REST API."
  value       = aws_api_gateway_rest_api.lambda_api.id
}

output "login_resource_id" {
  description = "The resource ID for /auth/login."
  value       = aws_api_gateway_resource.login_resource.id
}

output "signup_resource_id" {
  description = "The resource ID for /auth/signup."
  value       = aws_api_gateway_resource.signup_resource.id
}

output "login_post_method_id" {
  description = "The method ID for POST /auth/login."
  value       = aws_api_gateway_method.login_post.id
}

output "signup_post_method_id" {
  description = "The method ID for POST /auth/signup."
  value       = aws_api_gateway_method.signup_post.id
}
