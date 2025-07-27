import base64
import json
import os
import logging
from application.jwt_service import JWTService
from application.image_service import ImageService
from repository.s3_repository import S3Repository
from domain.models import ImageData, ImagePostRequest, ImagePostResponse, ImageUploadRequest, ImageDeleteRequest
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def lambda_handler(event, context):
    """
    AWS Lambda function for handling image upload and delete operations.
    """
    logger.info("Lambda function invoked")
    logger.debug(f"Full event: {json.dumps(event)}")
    
    try:
        logger.info("Initializing services")
        jwt_service = JWTService()
        s3_repository = S3Repository()
        image_service = ImageService(s3_repository)
        logger.info("Services initialized successfully")

        http_method = event.get('httpMethod', '').upper()
        logger.info(f"Processing {http_method} request")

        if http_method == 'GET':
            logger.info("Handling health check request")
            return _create_response(200, {
                "status": "OK",
                "message": "Service is operational"
            })
        
        headers = event.get('headers', {})
        auth_header = headers.get('Authorization') or headers.get('authorization')
        
        if not auth_header:
            logger.warning("Authorization header missing")
            return _create_response(401, {"error": "Authorization header missing"})
        
        logger.info("Decoding JWT token")
        user = jwt_service.decode_token(auth_header)
        logger.debug(f"Decoded user from token: {user}")
        if not user:
            logger.warning("Invalid or expired token")
            return _create_response(401, {"error": "Invalid or expired token"})
        logger.info(f"Authenticated user: {user.id}")

        if http_method == 'PUT':
            logger.info("Processing image upload")
            return _handle_upload(event, user, image_service)
        elif http_method == 'DELETE':
            logger.info("Processing image deletion")
            return _handle_delete(event, user, image_service)
        elif http_method == 'POST':
            logger.info("Processing image fetch (POST)")
            return _handle_post(user, image_service)
        else:
            logger.warning(f"Method not allowed: {http_method}")
            return _create_response(405, {"error": f"Method {http_method} not allowed"})
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return _create_response(500, {"error": "Internal server error"})


def _handle_upload(event, user, image_service):
    """Handle image upload"""
    logger.info("Starting upload process")
    try:
        logger.debug("Parsing image from event")
        image_data, file_extension = image_service.parse_image_from_event(event)
        
        if not image_data:
            logger.warning("No valid image data found in request")
            return _create_response(400, {"error": "No valid image data found in request"})
            
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {file_extension}")
            return _create_response(400, {"error": f"File type '{file_extension}' not allowed"})
        
        logger.info(f"Preparing upload request for user {user.id}")
        upload_request = ImageUploadRequest(
            user_id=user.id,
            image_data=image_data,
            content_type=f"image/{file_extension}",
            file_extension=file_extension
        )
        
        logger.debug("Uploading image to S3")
        response = image_service.upload_image(upload_request)
        
        if response.success:
            logger.info(f"Upload successful: {response.message}")
            return _create_response(200, {
                "message": response.message,
                "image_url": response.image_url,
                "user_id": user.id if user else None
            })
        else:
            logger.error(f"Upload failed: {response.message}")
            return _create_response(500, {"error": response.message})
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return _create_response(500, {"error": "Failed to upload image"})


def _handle_delete(event, user, image_service):
    """Handle image deletion"""
    logger.info("Starting deletion process")
    try:
        query_params = event.get('queryStringParameters') or {}
        image_name = query_params.get('image_name')
        
        if not image_name:
            logger.warning("Missing image_name parameter")
            return _create_response(400, {"error": "image_name parameter is required"})
        
        logger.info(f"Preparing delete request for image {image_name}")
        delete_request = ImageDeleteRequest(
            user_id=user.id,
            image_name=image_name
        )
        
        logger.debug("Deleting image from S3")
        response = image_service.delete_image(delete_request)
        
        if response.success:
            logger.info(f"Deletion successful: {response.message}")
            return _create_response(200, {
                "message": response.message,
                "user_id": user.id
            })
        else:
            error_level = "WARNING" if "not found" in response.message.lower() else "ERROR"
            getattr(logger, error_level.lower())(f"Deletion failed: {response.message}")
            return _create_response(404 if "not found" in response.message.lower() else 500, 
                                 {"error": response.message})
            
    except Exception as e:
        logger.error(f"Delete error: {str(e)}", exc_info=True)
        return _create_response(500, {"error": "Failed to delete image"})

def _handle_post(user, image_service):
    """Handle image fetch"""
    logger.info("Starting image fetch process")
    try:
        request = ImagePostRequest(user_id=user.id)
        images = image_service.get_all_images(request)

        response = ImagePostResponse(images=[
            ImageData(name=img.name, presigned_url=img.presigned_url) for img in images
        ])

        return _create_response(200, {
            "images": [
                {"name": img.name, "presigned_url": img.presigned_url}
                for img in response.images
            ]
        })
    
    except Exception as e:
        logger.error(f"Post fetch error: {str(e)}", exc_info=True)
        return _create_response(500, {"error": "Failed to fetch images"})


def _create_response(status_code, body):
    """Create standardized API Gateway response"""
    logger.debug(f"Creating response with status {status_code}")
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
