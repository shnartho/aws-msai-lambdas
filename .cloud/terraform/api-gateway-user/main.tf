data "aws_region" "current" {}

resource "aws_api_gateway_rest_api" "lambda_api" {
  name        = "${var.function_name}_api_${var.workspace}"
  description = "API Gateway for ${var.function_name} Lambda function"

  endpoint_configuration {
    types = ["REGIONAL"]
  }
}


######################
### Gateway Status ###
######################

# /status resource
resource "aws_api_gateway_resource" "status_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "status"
}

# GET method for /status
resource "aws_api_gateway_method" "status_get" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.status_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# Lambda integration for status GET
resource "aws_api_gateway_integration" "status_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.status_resource.id
  http_method             = aws_api_gateway_method.status_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


####################
### Gateway Auth ###
####################
resource "aws_api_gateway_resource" "lambda_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "auth"
}
## /auth/login resource
resource "aws_api_gateway_resource" "login_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.lambda_resource.id
  path_part   = "login"
}

## /auth/signup resource
resource "aws_api_gateway_resource" "signup_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.lambda_resource.id
  path_part   = "signup"
}
## POST method for /auth/login
resource "aws_api_gateway_method" "login_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.login_resource.id
  http_method   = "POST"
  authorization = "NONE"
  # api_key_required = true
}
## POST method for /auth/signup
resource "aws_api_gateway_method" "signup_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.signup_resource.id
  http_method   = "POST"
  authorization = "NONE"
  # api_key_required = true
}
## Lambda integration for /auth/login POST
resource "aws_api_gateway_integration" "login_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.login_resource.id
  http_method = aws_api_gateway_method.login_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambda_invoke_arn
}
## Lambda integration for /auth/signup POST
resource "aws_api_gateway_integration" "signup_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  resource_id = aws_api_gateway_resource.signup_resource.id
  http_method = aws_api_gateway_method.signup_post.http_method
  integration_http_method = "POST"
  type = "AWS_PROXY"
  uri = var.lambda_invoke_arn
}



####################
### Gateway User ###
####################

resource "aws_api_gateway_resource" "user_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "user"
}

# /user/balance resource
resource "aws_api_gateway_resource" "user_balance_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.user_resource.id
  path_part   = "balance"
}

# /user/profile resource
resource "aws_api_gateway_resource" "user_profile_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_resource.user_resource.id
  path_part   = "profile"
}

# PATCH method for /user/balance
resource "aws_api_gateway_method" "user_balance_patch" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.user_balance_resource.id
  http_method   = "PATCH"
  authorization = "NONE"
  # api_key_required = true
}

# GET method for /user/profile
resource "aws_api_gateway_method" "user_profile_get" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.user_profile_resource.id
  http_method   = "GET"
  authorization = "NONE"
  # api_key_required = true
}

# Lambda integration for /user/balance PATCH
resource "aws_api_gateway_integration" "user_balance_patch_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.user_balance_resource.id
  http_method             = aws_api_gateway_method.user_balance_patch.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Lambda integration for /user/profile GET
resource "aws_api_gateway_integration" "user_profile_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.user_profile_resource.id
  http_method             = aws_api_gateway_method.user_profile_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


######################
#### Gateway Ads #####
######################

# /ads resource
resource "aws_api_gateway_resource" "ads_resource" {
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  parent_id   = aws_api_gateway_rest_api.lambda_api.root_resource_id
  path_part   = "ads"
}

# GET method for /ads
resource "aws_api_gateway_method" "ads_get" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.ads_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# POST method for /ads
resource "aws_api_gateway_method" "ads_post" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.ads_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# PATCH method for /ads
resource "aws_api_gateway_method" "ads_patch" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.ads_resource.id
  http_method   = "PATCH"
  authorization = "NONE"
}

# DELETE method for /ads
resource "aws_api_gateway_method" "ads_delete" {
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  resource_id   = aws_api_gateway_resource.ads_resource.id
  http_method   = "DELETE"
  authorization = "NONE"
}

# Lambda integration for /ads GET
resource "aws_api_gateway_integration" "ads_get_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.ads_resource.id
  http_method             = aws_api_gateway_method.ads_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Lambda integration for /ads POST
resource "aws_api_gateway_integration" "ads_post_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.ads_resource.id
  http_method             = aws_api_gateway_method.ads_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Lambda integration for /ads PATCH
resource "aws_api_gateway_integration" "ads_patch_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.ads_resource.id
  http_method             = aws_api_gateway_method.ads_patch.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}

# Lambda integration for /ads DELETE
resource "aws_api_gateway_integration" "ads_delete_integration" {
  rest_api_id             = aws_api_gateway_rest_api.lambda_api.id
  resource_id             = aws_api_gateway_resource.ads_resource.id
  http_method             = aws_api_gateway_method.ads_delete.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.lambda_invoke_arn
}


##########################
### Gateway Deployment ###
##########################

## Lambda permission for API Gateway to invoke Lambda
resource "aws_lambda_permission" "apigw_user_invoke" {
  statement_id  = "AllowAPIGatewayInvokeUser"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.lambda_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "lambda_api_deployment" {
  depends_on = [
    aws_api_gateway_integration.login_post_integration,
    aws_api_gateway_integration.signup_post_integration,
    aws_api_gateway_integration.status_get_integration,
    aws_api_gateway_integration.user_balance_patch_integration,
    aws_api_gateway_integration.user_profile_get_integration,
    aws_api_gateway_integration.ads_get_integration,
    aws_api_gateway_integration.ads_post_integration,
    aws_api_gateway_integration.ads_patch_integration,
    aws_api_gateway_integration.ads_delete_integration
  ]
  rest_api_id = aws_api_gateway_rest_api.lambda_api.id
  stage_name  = var.workspace
}

# API Gateway stage (optional, for more control)
resource "aws_api_gateway_stage" "lambda_api_stage" {
  stage_name    = var.workspace
  rest_api_id   = aws_api_gateway_rest_api.lambda_api.id
  deployment_id = aws_api_gateway_deployment.lambda_api_deployment.id
}


#############################
### API Gateway Usage Plan ###
#############################
# resource "aws_api_gateway_usage_plan" "usage_limit" {
#   name = "global-limit"

#   api_stages {
#     api_id = aws_api_gateway_rest_api.lambda_api.id
#     stage  = aws_api_gateway_stage.lambda_api_stage.stage_name
#   }

#   throttle_settings {
#     rate_limit  = 1
#     burst_limit = 1
#   }

#   quota_settings {
#     limit  = 10
#     period = "DAY"
#   }
# }

# resource "aws_api_gateway_api_key" "user_key" {
#   name        = "user-api-key"
#   description = "API key for user usage plan"
#   enabled     = true
# }

# resource "aws_api_gateway_usage_plan_key" "user_key_plan" {
#   key_id        = aws_api_gateway_api_key.user_key.id
#   key_type      = "API_KEY"
#   usage_plan_id = aws_api_gateway_usage_plan.usage_limit.id
# }

