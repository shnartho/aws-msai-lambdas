import json
import logging
from domain.models import ImageData, ImagePostRequest, ImagePostResponse, ImageUploadRequest, ImageDeleteRequest
from config import Config

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

def handle_upload(event, user, image_service):
    """Handle image upload"""
    logger.info("Starting upload process")
    try:
        logger.debug("Parsing image from event")
        image_data, file_extension = image_service.parse_image_from_event(event)
        
        if not image_data:
            logger.warning("No valid image data found in request")
            return create_response(400, {"error": "No valid image data found in request"})
            
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {file_extension}")
            return create_response(400, {"error": f"File type '{file_extension}' not allowed"})
        
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
            return create_response(200, {
                "message": response.message,
                "image_url": response.image_url,
                "user_id": user.id if user else None
            })
        else:
            logger.error(f"Upload failed: {response.message}")
            return create_response(500, {"error": response.message})
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return create_response(500, {"error": "Failed to upload image"})


def handle_delete(image_name, user, image_service):
    """Handle image deletion"""
    logger.info("Starting deletion process")
    try:
        if not image_name:
            return create_response(400, {"error": "image name is required to delete"})
        
        logger.info(f"Preparing delete request for image {image_name}")
        delete_request = ImageDeleteRequest(
            user_id=user.id,
            image_name=image_name
        )
        
        logger.debug("Deleting image from S3")
        response = image_service.delete_image(delete_request)
        
        if response.success:
            return create_response(200, {
                "message": response.message,
                "user_id": user.id,
                "image_name": image_name
            })
        else:
            return create_response(404 if "not found" in response.message.lower() else 500, 
                                 {"error": response.message})
            
    except Exception as e:
        logger.error(f"Delete error: {str(e)}", exc_info=True)
        return create_response(500, {"error": "Failed to delete image"})

def handle_get_all_user_images(user, image_service):
    """Handle image fetch"""
    logger.info("Starting image fetch process")
    try:
        request = ImagePostRequest(user_id=user.id)
        images = image_service.get_all_user_images(request)

        response = ImagePostResponse(images=[
            ImageData(name=img.name, presigned_url=img.presigned_url) for img in images
        ])

        return create_response(200, {
            "images": [
                {"name": img.name, "presigned_url": img.presigned_url}
                for img in response.images
            ]
        })
    
    except Exception as e:
        logger.error(f"Post fetch error: {str(e)}", exc_info=True)
        return create_response(500, {"error": "Failed to fetch images"})
    
def handle_get_all_images(image_service):
    """Handle image fetch"""
    logger.info("Starting image fetch process")
    try:
        images = image_service.get_all_images()

        response = ImagePostResponse(images=[
            ImageData(name=img.name, presigned_url=img.presigned_url) for img in images
        ])

        return create_response(200, {
            "images": [
                {"name": img.name, "presigned_url": img.presigned_url}
                for img in response.images
            ]
        })
    
    except Exception as e:
        logger.error(f"Post fetch error: {str(e)}", exc_info=True)
        return create_response(500, {"error": "Failed to fetch images"})

def authenticate_user(headers, jwt_service):
    auth_header = headers.get('Authorization') or headers.get('authorization')
    if not auth_header:
        logger.warning("Authorization header missing")
        return None, create_response(401, {"error": "Authorization header missing"})

    user = jwt_service.decode_token(auth_header)
    if not user:
        logger.warning("Invalid or expired token")
        return None, create_response(401, {"error": "Invalid or expired token"})

    return user, None

def create_response(status_code, body):
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
