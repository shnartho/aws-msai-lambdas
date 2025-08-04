# output "api_gateway_url" {
#   description = "URL of the API Gateway endpoint for images"
#   value       = "https://${aws_api_gateway_rest_api.lambda_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.lambda_stage.stage_name}/images"
# }

# output "api_gateway_base_url" {
#   description = "Base URL of the API Gateway"
#   value       = "https://${aws_api_gateway_rest_api.lambda_api.id}.execute-api.${data.aws_region.current.name}.amazonaws.com/${aws_api_gateway_stage.lambda_stage.stage_name}"
# }

output "api_gateway_id" {
  description = "The ID of the API Gateway REST API."
  value       = aws_api_gateway_rest_api.lambda_api.id
}

output "login_resource_id" {
  description = "The resource ID for /user/login."
  value       = aws_api_gateway_resource.login_resource.id
}

output "signup_resource_id" {
  description = "The resource ID for /user/signup."
  value       = aws_api_gateway_resource.signup_resource.id
}

output "login_post_method_id" {
  description = "The method ID for POST /user/login."
  value       = aws_api_gateway_method.login_post.id
}

output "signup_post_method_id" {
  description = "The method ID for POST /user/signup."
  value       = aws_api_gateway_method.signup_post.id
}
