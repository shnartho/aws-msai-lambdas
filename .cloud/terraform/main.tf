// Image service module
module "lambda" {
  source        = "./lambda"
  workspace     = var.workspace
  function_name = "${var.function_base_name}_${var.workspace}"
  filename      = "releases/msai-image-uploader.zip"
  handler       = "main.lambda_handler"
  runtime       = "python3.11"
  timeout       = 60
  s3_bucket_name = "msai-images-bucket"
}

module "api_gateway" {
  source               = "./api-gateway"
  function_base_name   = var.function_base_name
  workspace            = var.workspace
  lambda_function_name = module.lambda.function_name
  lambda_invoke_arn    = module.lambda.invoke_arn
}

module "s3" {
  source       = "./s3"
  bucket_name  = "msai-images-bucket"
  environment  = var.workspace
  cors_origins = var.cors_origins
  aws_region   = var.aws_region
}

// Auth Service Module
module "lambda_auth" {
  source        = "./lambda-auth"
  workspace     = var.workspace
  function_name = "${var.function_name_auth_service}_${var.workspace}"
  filename      = "releases/msai-auth-service.zip"
  handler       = "bootstrap"
  runtime       = "provided.al2023"
  timeout       = 60
  dynamodb_user_table_arn = module.dynamodb_user.table_arn
}

module "api_gateway_auth" {
  source               = "./api-gateway-auth"
  function_name        = var.function_name_auth_service
  workspace            = var.workspace
  lambda_function_name = module.lambda_auth.function_name
  lambda_invoke_arn    = module.lambda_auth.invoke_arn
}

module "dynamodb_user" {
  source = "./dynamodb-user"
}
