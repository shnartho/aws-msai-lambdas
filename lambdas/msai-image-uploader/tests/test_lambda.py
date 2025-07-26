"""
Unit tests for the image uploader Lambda function using mocked AWS services.
Run with: pytest tests/
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import boto3
from moto import mock_aws
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import lambda_handler
from config import Config


class TestImageUploaderLambda:
    
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Set up environment variables for testing"""
        os.environ['JWT_SECRET_KEY'] = 'test-secret-key'
        os.environ['S3_BUCKET_NAME'] = 'test-bucket'
        
    def create_mock_event(self, method='POST', headers=None, body=None, query_params=None):
        """Helper to create mock API Gateway events"""
        if headers is None:
            headers = {}
            
        return {
            'httpMethod': method,
            'headers': headers,
            'queryStringParameters': query_params,
            'body': body,
            'isBase64Encoded': False,
            'requestContext': {
                'requestId': 'test-request-id'
            }
        }
    
    def create_mock_context(self):
        """Helper to create mock Lambda context"""
        context = Mock()
        context.function_name = 'msai-image-uploader'
        context.aws_request_id = 'test-request-id'
        return context
    
    @patch('application.jwt_service.JWTService.decode_token')
    def test_missing_authorization_header(self, mock_decode_token):
        """Test request without authorization header"""
        event = self.create_mock_event(method='POST')
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'Authorization header missing' in body['error']
        mock_decode_token.assert_not_called()
    
    @patch('application.jwt_service.JWTService.decode_token')
    def test_invalid_token(self, mock_decode_token):
        """Test request with invalid JWT token"""
        mock_decode_token.return_value = None
        
        headers = {'Authorization': 'Bearer invalid-token'}
        event = self.create_mock_event(method='POST', headers=headers)
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert 'Invalid or expired token' in body['error']
        mock_decode_token.assert_called_once()
    
    @patch('application.jwt_service.JWTService.decode_token')
    def test_unsupported_http_method(self, mock_decode_token):
        """Test unsupported HTTP method"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_decode_token.return_value = mock_user
        
        headers = {'Authorization': 'Bearer valid-token'}
        event = self.create_mock_event(method='GET', headers=headers)
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'Method GET not allowed' in body['error']
    
    @mock_aws
    @patch('application.jwt_service.JWTService.decode_token')
    @patch('application.image_service.ImageService.parse_image_from_event')
    @patch('application.image_service.ImageService.upload_image')
    def test_successful_image_upload(self, mock_upload, mock_parse, mock_decode_token):
        """Test successful image upload"""
        # Setup mocks
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_decode_token.return_value = mock_user
        
        mock_parse.return_value = (b'fake-image-data', 'png')
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.message = 'Image uploaded successfully'
        mock_response.image_url = 'https://s3.amazonaws.com/test-bucket/test-image.png'
        mock_upload.return_value = mock_response
        
        # Create event
        headers = {'Authorization': 'Bearer valid-token'}
        body = json.dumps({
            'image': 'base64-image-data',
            'filename': 'test.png'
        })
        event = self.create_mock_event(method='POST', headers=headers, body=body)
        context = self.create_mock_context()
        
        # Execute
        response = lambda_handler(event, context)
        
        # Assertions
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Image uploaded successfully'
        assert body['user_id'] == 'test-user-id'
        assert 'image_url' in body
    
    @patch('application.jwt_service.JWTService.decode_token')
    @patch('application.image_service.ImageService.parse_image_from_event')
    def test_upload_invalid_file_type(self, mock_parse, mock_decode_token):
        """Test upload with invalid file type"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_decode_token.return_value = mock_user
        
        mock_parse.return_value = (b'fake-image-data', 'exe')  # Invalid extension
        
        headers = {'Authorization': 'Bearer valid-token'}
        body = json.dumps({
            'image': 'base64-image-data',
            'filename': 'malware.exe'
        })
        event = self.create_mock_event(method='POST', headers=headers, body=body)
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'File type \'exe\' not allowed' in body['error']
    
    @patch('application.jwt_service.JWTService.decode_token')
    @patch('application.image_service.ImageService.delete_image')
    def test_successful_image_deletion(self, mock_delete, mock_decode_token):
        """Test successful image deletion"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_decode_token.return_value = mock_user
        
        mock_response = Mock()
        mock_response.success = True
        mock_response.message = 'Image deleted successfully'
        mock_delete.return_value = mock_response
        
        headers = {'Authorization': 'Bearer valid-token'}
        query_params = {'image_name': 'test-image.png'}
        event = self.create_mock_event(method='DELETE', headers=headers, query_params=query_params)
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'Image deleted successfully'
        assert body['user_id'] == 'test-user-id'
    
    @patch('application.jwt_service.JWTService.decode_token')
    def test_delete_missing_image_name(self, mock_decode_token):
        """Test delete request without image_name parameter"""
        mock_user = Mock()
        mock_user.id = 'test-user-id'
        mock_decode_token.return_value = mock_user
        
        headers = {'Authorization': 'Bearer valid-token'}
        event = self.create_mock_event(method='DELETE', headers=headers)
        context = self.create_mock_context()
        
        response = lambda_handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'image_name parameter is required' in body['error']


if __name__ == '__main__':
    pytest.main([__file__])
