import json
import logging
from application.jwt_service import JWTService
from application.image_service import ImageService
from repository.s3_repository import S3Repository
from domain.models import ImageData, ImagePostRequest, ImagePostResponse, ImageUploadRequest, ImageDeleteRequest
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def lambda_handler(event, context):
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

        headers = event.get('headers', {})
        header_fetch_all_images = headers.get('x-fetch-all-images')
        header_fetch_user_iamges = headers.get('x-fetch-user-images')
        header_region = headers.get('x-region')
        header_delete_image_name = headers.get('x-delete-image-name')

        if http_method == 'GET':
            if header_fetch_all_images is None and header_region is None and header_fetch_user_iamges is None:
                logger.info("Handling health check request")
                return _create_response(200, {
                    "status": "OK",
                    "message": "Service is operational"
                })
            if header_fetch_all_images and header_fetch_user_iamges:
                return _create_response(400, {"error": "Only one of x-fetch-all-images or x-fetch-user-images can be set"})
            elif header_fetch_all_images and header_fetch_all_images == 'true':
                if not header_region or header_region.upper() not in Config.ALLOWED_REGIONS.split(','):
                    return _create_response(403, {"error": f"Region {header_region} not allowed"})
                logger.info(f"Fetching all images from region: {header_region}")
                return _handle_get_all_images(image_service)
            elif header_fetch_user_iamges and header_fetch_user_iamges == 'true':
                user, error_response = authenticate_user(headers, jwt_service)
                if error_response:
                    return error_response
                logger.info(f"Fetching images for user: {user.id}")
                return _handle_get_all_user_images(user, image_service)
            else:
                logger.warning("Invalid headers for GET request")
                return _create_response(400, {"error": "Invalid headers for GET request"})

        user, error_response = authenticate_user(headers, jwt_service)
        if error_response:
            return error_response

        if http_method == 'PUT':
            logger.info("Processing image upload")
            return _handle_upload(event, user, image_service)
        elif http_method == 'DELETE':
            if not header_delete_image_name:
                return _create_response(400, {"error": "x-delete-image-name header is required"})
            if not str(header_delete_image_name).endswith(('.jpg', '.jpeg', '.png')):
                return _create_response(400, {"error": "Invalid image name format. Allowed formats: .jpg, .jpeg, .png"})
            logger.info("Processing image deletion")
            return _handle_delete(header_delete_image_name, user, image_service)
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


def _handle_delete(image_name, user, image_service):
    """Handle image deletion"""
    logger.info("Starting deletion process")
    try:
        if not image_name:
            return _create_response(400, {"error": "image name is required to delete"})
        
        logger.info(f"Preparing delete request for image {image_name}")
        delete_request = ImageDeleteRequest(
            user_id=user.id,
            image_name=image_name
        )
        
        logger.debug("Deleting image from S3")
        response = image_service.delete_image(delete_request)
        
        if response.success:
            return _create_response(200, {
                "message": response.message,
                "user_id": user.id,
                "image_name": image_name
            })
        else:
            return _create_response(404 if "not found" in response.message.lower() else 500, 
                                 {"error": response.message})
            
    except Exception as e:
        logger.error(f"Delete error: {str(e)}", exc_info=True)
        return _create_response(500, {"error": "Failed to delete image"})

def _handle_get_all_user_images(user, image_service):
    """Handle image fetch"""
    logger.info("Starting image fetch process")
    try:
        request = ImagePostRequest(user_id=user.id)
        images = image_service.get_all_user_images(request)

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
    
def _handle_get_all_images(image_service):
    """Handle image fetch"""
    logger.info("Starting image fetch process")
    try:
        images = image_service.get_all_images()

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

def authenticate_user(headers, jwt_service):
    auth_header = headers.get('Authorization') or headers.get('authorization')
    if not auth_header:
        logger.warning("Authorization header missing")
        return None, _create_response(401, {"error": "Authorization header missing"})

    user = jwt_service.decode_token(auth_header)
    if not user:
        logger.warning("Invalid or expired token")
        return None, _create_response(401, {"error": "Invalid or expired token"})

    return user, None

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
