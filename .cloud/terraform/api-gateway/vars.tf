variable "function_base_name" {
  description = "Base name for the function"
  type        = string
}

variable "workspace" {
  description = "The workspace environment (dev, prod, etc.)"
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