resource "aws_dynamodb_table" "ads" {
  name           = "msai.ads"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "id"

  attribute {
    name = "id"
    type = "S"
  }

  attribute {
    name = "reward_per_view"
    type = "N"
  }

  global_secondary_index {
    name               = "reward_per_view-index"
    hash_key           = "reward_per_view"
    projection_type    = "ALL"
  }
}
