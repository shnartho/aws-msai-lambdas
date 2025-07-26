variable "workspace" {
  description = "The workspace environment (e.g., dev, prod)"
  type        = string
}

variable "function_base_name" {
  description = "Base name for the Lambda function"
  type        = string
  default     = "hello_world_lambda"
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "cors_origins" {
  description = "List of allowed CORS origins for S3 bucket"
  type        = list(string)
  default     = ["*"]
}