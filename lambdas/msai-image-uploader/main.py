import json
import os
from application.jwt_service import JWTService
from application.image_service import ImageService
from repository.s3_repository import S3Repository
from domain.models import ImageUploadRequest, ImageDeleteRequest
from config import Config


def lambda_handler(event, context):
    """
    AWS Lambda function for handling image upload and delete operations.
    
    Args:
        event: The event data passed to the Lambda function
        context: The runtime information provided by AWS Lambda
        
    Returns:
        A dictionary containing a status code and response formatted for API Gateway
    """
    
    jwt_service = JWTService()
    s3_repository = S3Repository()
    image_service = ImageService(s3_repository)
    
    try:
        http_method = event.get('httpMethod', '').upper()
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            return _create_response(401, {"error": "Authorization header missing"})
        
        user = jwt_service.decode_token(auth_header)
        if not user:
            return _create_response(401, {"error": "Invalid or expired token"})
        
        if http_method == 'POST':
            return _handle_upload(event, user, image_service)
        elif http_method == 'DELETE':
            return _handle_delete(event, user, image_service)
        else:
            return _create_response(405, {"error": f"Method {http_method} not allowed"})
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return _create_response(500, {"error": "Internal server error"})


def _handle_upload(event, user, image_service):
    """Handle image upload"""
    try:
        image_data, file_extension = image_service.parse_image_from_event(event)
        
        if not image_data:
            return _create_response(400, {"error": "No valid image data found in request"})
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            return _create_response(400, {"error": f"File type '{file_extension}' not allowed"})
        
        upload_request = ImageUploadRequest(
            user_id=user.id,
            image_data=image_data,
            content_type=f"image/{file_extension}",
            file_extension=file_extension
        )
        
        response = image_service.upload_image(upload_request)
        
        if response.success:
            return _create_response(200, {
                "message": response.message,
                "image_url": response.image_url,
                "user_id": user.id
            })
        else:
            return _create_response(500, {"error": response.message})
            
    except Exception as e:
        print(f"Upload error: {str(e)}")
        return _create_response(500, {"error": "Failed to upload image"})


def _handle_delete(event, user, image_service):
    """Handle image deletion"""
    try:
        query_params = event.get('queryStringParameters') or {}
        image_name = query_params.get('image_name')
        
        if not image_name:
            return _create_response(400, {"error": "image_name parameter is required"})
        
        delete_request = ImageDeleteRequest(
            user_id=user.id,
            image_name=image_name
        )
        
        response = image_service.delete_image(delete_request)
        
        if response.success:
            return _create_response(200, {
                "message": response.message,
                "user_id": user.id
            })
        else:
            return _create_response(404 if "not found" in response.message.lower() else 500, 
                                 {"error": response.message})
            
    except Exception as e:
        print(f"Delete error: {str(e)}")
        return _create_response(500, {"error": "Failed to delete image"})


def _create_response(status_code, body):
    """Create standardized API Gateway response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        },
        'body': json.dumps(body)
    }
