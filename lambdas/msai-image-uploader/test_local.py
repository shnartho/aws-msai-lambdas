"""
Local testing script for the image uploader Lambda function.
This script sets up the environment and simulates API Gateway events to test the Lambda function locally.
"""

import json
import os
import sys
import subprocess
from main import lambda_handler


def create_mock_event(method='POST', headers=None, body=None, query_params=None):
    """Create a mock API Gateway event"""
    if headers is None:
        headers = {}
    
    event = {
        'httpMethod': method,
        'headers': headers,
        'queryStringParameters': query_params,
        'body': body,
        'isBase64Encoded': False
    }
    
    return event


def create_mock_context():
    """Create a mock Lambda context"""
    class MockContext:
        def __init__(self):
            self.function_name = 'msai-image-uploader'
            self.function_version = '1'
            self.invoked_function_arn = 'arn:aws:lambda:us-east-1:123456789012:function:msai-image-uploader'
            self.memory_limit_in_mb = 128
            self.remaining_time_in_millis = 30000
            self.log_group_name = '/aws/lambda/msai-image-uploader'
            self.log_stream_name = '2025/06/10/test-stream'
            self.aws_request_id = 'test-request-id'
    
    return MockContext()


def test_upload_image():
    """Test image upload functionality"""
    print("Testing image upload...")
    
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJpYXQiOjE2MzQ1Njc4OTAsImV4cCI6OTk5OTk5OTk5OX0.test-signature',
        'Content-Type': 'application/json'
    }
    
    # Sample 1x1 pixel PNG image (base64)
    sample_image = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
    
    body = json.dumps({
        'image': sample_image,
        'filename': 'test.png'
    })
    
    event = create_mock_event('POST', headers, body)
    
    try:
        response = lambda_handler(event, create_mock_context())
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def test_delete_image():
    """Test image deletion functionality"""
    print("Testing image deletion...")
    
    headers = {
        'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0LXVzZXItaWQiLCJpYXQiOjE2MzQ1Njc4OTAsImV4cCI6OTk5OTk5OTk5OX0.test-signature'
    }
    
    query_params = {'image_name': 'test-image.png'}
    event = create_mock_event('DELETE', headers, query_params=query_params)
    
    try:
        response = lambda_handler(event, create_mock_context())
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def test_unauthorized_request():
    """Test unauthorized request"""
    print("Testing unauthorized request...")
    
    event = create_mock_event('POST')
    
    try:
        response = lambda_handler(event, create_mock_context())
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def test_invalid_method():
    """Test invalid HTTP method"""
    print("Testing invalid HTTP method...")
    
    headers = {'Authorization': 'Bearer test-token'}
    event = create_mock_event('GET', headers)
    
    try:
        response = lambda_handler(event, create_mock_context())
        print(f"Response: {json.dumps(response, indent=2)}")
        return response
    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def setup_environment():
    """Set up environment variables for testing"""
    print("Setting up test environment...")
    
    env_vars = {
        'JWT_SECRET_KEY': 'test-secret-key-change-in-production',
        'S3_BUCKET_NAME': 'test-bucket-name',
        'AWS_DEFAULT_REGION': 'us-east-1'
    }
    
    for key, value in env_vars.items():
        if not os.environ.get(key):
            os.environ[key] = value
            print(f"✓ Set {key}")
        else:
            print(f"✓ {key} already configured")


def install_deps():
    """Install dependencies if needed"""
    try:
        import boto3
        print("✓ Dependencies available")
        return True
    except ImportError:
        print("Installing dependencies...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'boto3'], check=True)
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install dependencies")
            return False


if __name__ == '__main__':
    print("=" * 50)
    print("AWS LAMBDA IMAGE UPLOADER - LOCAL TESTING")
    print("=" * 50)
    
    # Setup environment and dependencies
    if not install_deps():
        sys.exit(1)
    
    setup_environment()
    
    print("\nRunning tests...")
    print("-" * 30)
    
    # Run all tests
    test_unauthorized_request()
    print("-" * 30)
    
    test_invalid_method()
    print("-" * 30)
    
    test_upload_image()
    print("-" * 30)
    
    test_delete_image()
    print("-" * 30)
    
    print("✓ Testing completed!")
    print("\nFor advanced testing, install AWS SAM CLI:")
    print("- sam local start-api")
    print("- sam local invoke -e events/upload_event.json")
