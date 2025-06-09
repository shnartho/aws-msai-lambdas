variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "filename" {
  description = "Path to the deployment package ZIP file"
  type        = string
}

variable "handler" {
  description = "Function entrypoint in your code"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime (e.g., nodejs18.x, python3.9)"
  type        = string
}

variable "role_arn" {
  description = "IAM role ARN for the Lambda function"
  type        = string
}
