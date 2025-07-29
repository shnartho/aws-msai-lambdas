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

variable "timeout" {
  description = "The amount of time your Lambda Function has to run in seconds"
  type        = number
  default     = 15  # Default to 3 seconds if not specified
}

variable "workspace" {
  description = "The workspace/environment name"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for Lambda permissions"
  type        = string
}