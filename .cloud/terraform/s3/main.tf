# S3 Bucket for MSAI Image Uploader
resource "aws_s3_bucket" "msai_images_bucket" {
  bucket = var.bucket_name

  tags = {
    Name        = "MSAI Images Bucket"
    Environment = var.environment
    Project     = "msai-lambdas"
  }
}

# S3 Bucket Versioning
resource "aws_s3_bucket_versioning" "msai_images_bucket_versioning" {
  bucket = aws_s3_bucket.msai_images_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Bucket Server Side Encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "msai_images_bucket_encryption" {
  bucket = aws_s3_bucket.msai_images_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 Bucket Public Access Block
resource "aws_s3_bucket_public_access_block" "msai_images_bucket_pab" {
  bucket = aws_s3_bucket.msai_images_bucket.id

  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

# S3 Bucket Policy for public read access to images
resource "aws_s3_bucket_policy" "msai_images_bucket_policy" {
  bucket = aws_s3_bucket.msai_images_bucket.id
  depends_on = [aws_s3_bucket_public_access_block.msai_images_bucket_pab]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${aws_s3_bucket.msai_images_bucket.arn}/*"
      }
    ]
  })
}

# S3 Bucket CORS Configuration
resource "aws_s3_bucket_cors_configuration" "msai_images_bucket_cors" {
  bucket = aws_s3_bucket.msai_images_bucket.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE", "HEAD"]
    allowed_origins = var.cors_origins
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 Bucket Lifecycle Configuration
resource "aws_s3_bucket_lifecycle_configuration" "msai_images_bucket_lifecycle" {
  bucket = aws_s3_bucket.msai_images_bucket.id

  rule {
    id     = "delete_old_versions"
    status = "Enabled"

    filter {}

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }

  rule {
    id     = "transition_to_ia"
    status = "Enabled"

    filter {}

    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}