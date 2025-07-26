variable "bucket_name" {
  description = "Name of the S3 bucket for storing images"
  type        = string
  default     = "msai-images-bucket"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "cors_origins" {
  description = "List of allowed CORS origins"
  type        = list(string)
  default     = ["*"]
}

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}