variable "workspace" {
  description = "The workspace environment (e.g., dev, prod)"
  type        = string
}

variable "function_base_name" {
  description = "Base name for the Lambda function"
  type        = string
  default     = "msai-image-service"
}

variable "function_name_user_service" {
  description = "Base name for the Lambda function"
  type        = string
  default     = "msai-user-service"
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

variable "deploy_service" {
  description = "Which service to deploy: 'auth', 'image', or 'all'"
  type        = string
  default     = "all"
}