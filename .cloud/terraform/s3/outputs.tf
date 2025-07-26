output "bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.msai_images_bucket.id
}

output "bucket_arn" {
  description = "ARN of the S3 bucket"
  value       = aws_s3_bucket.msai_images_bucket.arn
}

output "bucket_domain_name" {
  description = "Domain name of the S3 bucket"
  value       = aws_s3_bucket.msai_images_bucket.bucket_domain_name
}

output "bucket_regional_domain_name" {
  description = "Regional domain name of the S3 bucket"
  value       = aws_s3_bucket.msai_images_bucket.bucket_regional_domain_name
}

output "bucket_hosted_zone_id" {
  description = "Hosted zone ID of the S3 bucket"
  value       = aws_s3_bucket.msai_images_bucket.hosted_zone_id
}

output "bucket_website_endpoint" {
  description = "Website endpoint of the S3 bucket"
  value       = "https://${aws_s3_bucket.msai_images_bucket.bucket_domain_name}"
}