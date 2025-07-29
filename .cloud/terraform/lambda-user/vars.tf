variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "filename" {
  description = "Path to the deployment package zip file"
  type        = string
}

variable "handler" {
  description = "Lambda handler function"
  type        = string
}

variable "runtime" {
  description = "Lambda runtime environment"
  type        = string
}

variable "timeout" {
  description = "Lambda function timeout in seconds"
  type        = number
  default     = 60
}

variable "workspace" {
  description = "Deployment workspace/environment name"
  type        = string
}

variable "dynamodb_user_table_arn" {
  description = "ARN of the msai.user DynamoDB table"
  type        = string
}

variable "dynamodb_ads_table_arn" {
  description = "ARN of the msai.ads DynamoDB table"
  type        = string
}
