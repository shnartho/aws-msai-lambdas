output "table_name" {
  value = aws_dynamodb_table.user.name
}

output "table_arn" {
  value = aws_dynamodb_table.user.arn
}
