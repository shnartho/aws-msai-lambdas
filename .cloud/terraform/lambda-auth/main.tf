resource "aws_lambda_function" "lambda" {
  function_name = var.function_name
  filename      = var.filename
  handler       = var.handler
  runtime       = var.runtime
  role          = aws_iam_role.lambda_execution_role.arn
  timeout       = var.timeout
}

# Create IAM role for Lambda execution
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.function_name}_execution_role_${var.workspace}"

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

# Allow Lambda to access DynamoDB table msai.user
resource "aws_iam_policy" "dynamodb_user_access" {
  name        = "lambda_auth_dynamodb_user_access_${var.workspace}"
  description = "Allow Lambda to access msai.user DynamoDB table"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:GetItem",
          "dynamodb:UpdateItem",
          "dynamodb:Query"
        ]
        Resource = [
          "${var.dynamodb_user_table_arn}",
          "${var.dynamodb_user_table_arn}/index/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_dynamodb_user_access" {
  policy_arn = aws_iam_policy.dynamodb_user_access.arn
  role       = aws_iam_role.lambda_execution_role.name
}
