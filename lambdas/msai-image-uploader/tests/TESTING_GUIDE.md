# Local Testing Guide for AWS Lambda Image Uploader

This guide explains how to test your AWS Lambda function locally using Poetry and various testing methods.

## Prerequisites

1. **Python 3.9+** installed
2. **Poetry** package manager (`curl -sSL https://install.python-poetry.org | python3 -`)
3. **AWS credentials** configured (for S3 operations)

## Quick Start

1. **Install dependencies:**
   ```powershell
   poetry install
   ```

   For production dependencies only:
   ```powershell
   poetry install --without dev
   ```

2. **Set environment variables:**
   ```powershell
   $env:JWT_SECRET_KEY = "your-secret-key"
   $env:S3_BUCKET_NAME = "your-test-bucket"
   $env:AWS_DEFAULT_REGION = "us-east-1"
   ```

3. **Run basic tests:**
   ```powershell
   poetry run python test_local.py
   ```

## Testing Methods

### Method 1: Simple Local Testing Script

The `test_local.py` script provides basic testing functionality:

```powershell
poetry run python test_local.py
```

This script tests:
- ✅ Unauthorized requests
- ✅ Invalid HTTP methods
- ✅ Image upload functionality
- ✅ Image deletion functionality

### Method 2: Unit Tests with Mocking

Run comprehensive unit tests:

```powershell
poetry run pytest tests/ -v
```

Features:
- ✅ Mocked AWS services (no real AWS calls)
- ✅ Isolated testing of individual components
- ✅ Coverage of edge cases and error scenarios

### Method 3: AWS SAM CLI (Advanced)

For production-like testing, install AWS SAM CLI:

1. **Install SAM CLI:**
   - Download from: https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html

2. **Start local API:**
   ```powershell
   sam local start-api
   ```

3. **Test with curl:**
   ```powershell
   curl -X POST http://localhost:3000/upload `
     -H "Authorization: Bearer your-jwt-token" `
     -H "Content-Type: application/json" `
     -d '{"image": "base64-image-data", "filename": "test.png"}'
   ```

4. **Invoke function directly:**
   ```powershell
   sam local invoke -e events/upload_event.json
   ```

## Test Data

### Sample JWT Token
For testing, you can use this sample JWT token structure:
```json
{
  "sub": "test-user-id",
  "iat": 1634567890,
  "exp": 9999999999
}
```

### Sample Image Data
The test files include a small base64-encoded PNG image for testing uploads.

### Sample Events
Check the `events/` directory for:
- `upload_event.json` - Image upload test event
- `delete_event.json` - Image deletion test event

## Additional Poetry Commands

### Environment Management

```powershell
# Show the virtual environment path
poetry env info

# Activate the virtual environment (Poetry 2.0+)
poetry env activate

# Show which Python is being used
poetry run python --version

# Run any command in the Poetry environment
poetry run <command>
```

### Development Commands

```powershell
# Format code with Black
poetry run black .

# Lint code with flake8
poetry run flake8 .

# Type checking with mypy
poetry run mypy .

# Add a new dependency
poetry add requests

# Add a development dependency
poetry add --group dev pytest-cov

# Update dependencies
poetry update

# Show dependency tree
poetry show --tree
```

### Testing with Coverage

```powershell
# Install coverage tool
poetry add --group dev pytest-cov

# Run tests with coverage
poetry run pytest --cov=application --cov=domain --cov=repository tests/

# Generate HTML coverage report
poetry run pytest --cov=application --cov-report=html tests/
```

## Environment Variables

You can set environment variables in several ways:

### Option 1: PowerShell Session
```powershell
$env:JWT_SECRET_KEY = "your-secret-key"
$env:S3_BUCKET_NAME = "your-test-bucket"
$env:AWS_DEFAULT_REGION = "us-east-1"
```

### Option 2: .env File
Create a `.env` file in the project root:
```
JWT_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=your-test-bucket
AWS_DEFAULT_REGION=us-east-1
```

Then use `python-dotenv` to load it:
```python
from dotenv import load_dotenv
load_dotenv()
```

## AWS Configuration

### Option 1: AWS Credentials File
Create `~/.aws/credentials`:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

### Option 2: Environment Variables
```powershell
$env:AWS_ACCESS_KEY_ID = "your-access-key"
$env:AWS_SECRET_ACCESS_KEY = "your-secret-key"
```

### Option 3: IAM Role (if running on EC2)
The Lambda will automatically use the instance's IAM role.

## Testing Different Scenarios

### 1. Valid Image Upload
```json
{
  "httpMethod": "POST",
  "headers": {
    "Authorization": "Bearer valid-jwt-token"
  },
  "body": "{\"image\": \"base64-image-data\", \"filename\": \"test.png\"}"
}
```

### 2. Image Deletion
```json
{
  "httpMethod": "DELETE",
  "headers": {
    "Authorization": "Bearer valid-jwt-token"
  },
  "queryStringParameters": {
    "image_name": "test-image.png"
  }
}
```

### 3. Unauthorized Request
```json
{
  "httpMethod": "POST",
  "headers": {},
  "body": "{\"image\": \"base64-image-data\"}"
}
```

## Debugging

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check CloudWatch Logs Locally
When using SAM CLI, logs are displayed in the terminal.

### Validate JWT Tokens
Use online JWT decoders or:
```python
import jwt
decoded = jwt.decode(token, 'your-secret', algorithms=['HS256'])
print(decoded)
```

## Common Issues and Solutions

### 1. Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python path and virtual environment

### 2. AWS Credential Issues
- Verify AWS credentials are configured
- Check IAM permissions for S3 operations
- Ensure S3 bucket exists and is accessible

### 3. JWT Token Issues
- Verify JWT_SECRET_KEY matches the one used to sign tokens
- Check token expiration
- Validate token format

### 4. S3 Permission Errors
Required S3 permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::your-bucket/*"
    }
  ]
}
```

## Performance Testing

### Load Testing with Artillery (Optional)
1. Install Artillery: `npm install -g artillery`
2. Create test config and run load tests

### Memory and Timeout Testing
- Monitor function execution time
- Test with various image sizes
- Verify memory usage patterns

## Next Steps

1. **Integration Testing:** Test with real API Gateway and S3
2. **Security Testing:** Validate JWT security and input sanitization
3. **Performance Optimization:** Profile and optimize cold start times
4. **Monitoring:** Set up CloudWatch dashboards and alarms

## Troubleshooting

If you encounter issues:

1. Check the logs output from test scripts
2. Verify environment variables are set correctly
3. Ensure AWS credentials have proper permissions
4. Validate that the S3 bucket exists and is accessible
5. Check that JWT tokens are properly formatted and not expired

For additional help, refer to the AWS Lambda and SAM CLI documentation.
