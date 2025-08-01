import base64
import json
from domain.models import ImageData, ImageUploadRequest, ImageUploadResponse, ImageDeleteRequest, ImageDeleteResponse, ImagePostRequest, ImagePostResponse
from repository.s3_repository import S3Repository
import logging

logger = logging.getLogger()
logger.setLevel(logging.WARNING)

class ImageService:
    """Service for handling image operations"""
    
    def __init__(self, s3_repository: S3Repository):
        self.s3_repository = s3_repository
    
    def upload_image(self, request: ImageUploadRequest) -> ImageUploadResponse:
        """
        Upload image to S3
        
        Args:
            request: ImageUploadRequest object
            
        Returns:
            ImageUploadResponse object
        """
        try:
            success, image_url, message = self.s3_repository.upload_image(
                user_id=request.user_id,
                image_data=request.image_data,
                file_extension=request.file_extension
            )
            
            return ImageUploadResponse(
                success=success,
                image_url=image_url,
                message=message,
                user_id=request.user_id
            )
            
        except Exception as e:
            return ImageUploadResponse(
                success=False,
                image_url="",
                message=f"Service error: {str(e)}",
                user_id=request.user_id
            )
    
    def delete_image(self, request: ImageDeleteRequest) -> ImageDeleteResponse:
        """
        Delete image from S3
        
        Args:
            request: ImageDeleteRequest object
            
        Returns:
            ImageDeleteResponse object
        """
        try:
            success, message = self.s3_repository.delete_image(
                user_id=request.user_id,
                image_name=request.image_name
            )

            return ImageDeleteResponse(
                success=success,
                message=message,
                user_id=request.user_id
            )
            
        except Exception as e:
            return ImageDeleteResponse(
                success=False,
                message=f"Service error: {str(e)}",
                user_id=request.user_id
            )
        
    def get_all_user_images(self, request: ImagePostRequest) -> list[ImageData]:
        """
        Fetch all user images for a user from S3
        
        Args:
            request: ImagePostRequest
        
        Returns:
            List of ImageData
        """
        try:
            logger.info(f"Fetching all images for user: {request.user_id}")
            objects = self.s3_repository.list_user_images(request.user_id)
            logger.info(f"Found {len(objects)} images for user: {request.user_id}")

            images = []
            for obj in objects:
                image_name = obj['Key'].split('/')[-1]
                presigned_url = self.s3_repository.get_presigned_url(obj['Key'])

                if presigned_url:
                    images.append(ImageData(name=image_name, presigned_url=presigned_url))

            return images

        except Exception as e:
            logger.error(f"get_all_user_images: {str(e)}", exc_info=True)
            return []
        
    def get_all_images(self) -> list[ImageData]:
        try:
            logger.info("Fetching all images from S3")
            objects = self.s3_repository.list_all_images()
            logger.info(f"Found {len(objects)} images in total")

            images = []
            for obj in objects:
                if obj.get('Size', 0) == 0:
                    continue # Skip empty objects 
                image_name = obj['Key'].split('/')[-1]
                presigned_url = self.s3_repository.get_presigned_url(obj['Key'])

                if presigned_url:
                    images.append(ImageData(name=image_name, presigned_url=presigned_url))

            return images

        except Exception as e:
            logger.error(f"get_all_images: {str(e)}", exc_info=True)
            return []
        
    
    def parse_image_from_event(self, event: dict):
        logger.info("parse_image_from_event: called")

        try:
            if 'body' not in event:
                logger.warning("parse_image_from_event: 'body' not in event")
                return None, None

            body = event['body']
            logger.info(f"parse_image_from_event: body type before decode = {type(body)}")
            logger.info(f"parse_image_from_event: isBase64Encoded = {event.get('isBase64Encoded')}")

            if event.get('isBase64Encoded', False):
                try:
                    body = base64.b64decode(body)
                    logger.info("parse_image_from_event: base64 body decoded successfully")
                except Exception as e:
                    logger.error(f"Failed to base64 decode body: {str(e)}")
                    return None, None

            if isinstance(body, (bytes, bytearray)):
                logger.info("parse_image_from_event: body is bytes")
                return body, 'jpg'

            if isinstance(body, str):
                logger.info("parse_image_from_event: body is str, trying json.loads")
                try:
                    json_body = json.loads(body)
                    logger.info("parse_image_from_event: JSON loaded successfully")
                    if 'image' in json_body and 'filename' in json_body:
                        image_data = base64.b64decode(json_body['image'])
                        filename = json_body['filename']
                        file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
                        logger.info(f"parse_image_from_event: decoded image from JSON, extension = {file_extension}")
                        return image_data, file_extension
                except Exception as e:
                    logger.warning(f"parse_image_from_event: failed json.loads: {str(e)}")

                logger.info("parse_image_from_event: fallback base64 decode for raw string")
                try:
                    image_data = base64.b64decode(body)
                    logger.info("parse_image_from_event: fallback base64 decode succeeded")
                    return image_data, 'jpg'
                except Exception as e:
                    logger.warning(f"parse_image_from_event: fallback base64 decode failed: {str(e)}")
                    return None, None

            logger.warning("parse_image_from_event: unsupported body type")
            return None, None

        except Exception as e:
            logger.error(f"parse_image_from_event: fatal error: {str(e)}")
            return None, None
