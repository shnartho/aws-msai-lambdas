module "lambda" {
  source        = "./lambda"
  function_name = "${var.function_base_name}_${var.workspace}"
  filename      = "releases/msai-image-uploader.zip"
  handler       = "main.lambda_handler"
  runtime       = "python3.11"
  role_arn      = aws_iam_role.lambda_execution_role.arn
}

# Create IAM role for Lambda execution
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.function_base_name}_execution_role_${var.workspace}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach basic Lambda execution policy
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

module "api_gateway" {
  source               = "./api-gateway"
  function_base_name   = var.function_base_name
  workspace           = var.workspace
  lambda_function_name = module.lambda.function_name
  lambda_invoke_arn   = module.lambda.invoke_arn
}

# S3 bucket module for image uploads
module "s3" {
  source = "./s3"
  
  bucket_name   = "msai-images-bucket"
  environment   = var.workspace
  cors_origins  = var.cors_origins
  aws_region    = var.aws_region
}
