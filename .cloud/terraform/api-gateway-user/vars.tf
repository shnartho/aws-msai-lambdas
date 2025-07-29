variable "function_name" {
  description = "Name of the Lambda function (e.g., msai-user-service)"
  type        = string
}

variable "workspace" {
  description = "Workspace/environment name (e.g., dev, prod)"
  type        = string
}

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "lambda_invoke_arn" {
  description = "Invoke ARN of the Lambda function"
  type        = string
}