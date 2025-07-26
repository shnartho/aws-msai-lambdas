import base64
import json
from typing import Tuple, Optional
from domain.models import ImageUploadRequest, ImageUploadResponse, ImageDeleteRequest, ImageDeleteResponse
from repository.s3_repository import S3Repository


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
                message=message
            )
            
        except Exception as e:
            return ImageUploadResponse(
                success=False,
                image_url="",
                message=f"Service error: {str(e)}"
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
                message=message
            )
            
        except Exception as e:
            return ImageDeleteResponse(
                success=False,
                message=f"Service error: {str(e)}"
            )

    
    def parse_image_from_event(self, event: dict) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Parse image data from Lambda event
        
        Args:
            event: Lambda event dictionary
            
        Returns:
            Tuple of (image_data, file_extension) or (None, None) if parsing fails
        """
        try:
            if 'body' not in event:
                print("No body in event")
                return None, None
            
            body = event['body']
            
            if event.get('isBase64Encoded', False):
                body = base64.b64decode(body).decode('utf-8')
            
            try:
                json_body = json.loads(body) if isinstance(body, str) else body
                
                if 'image' in json_body and 'filename' in json_body:
                    image_data = base64.b64decode(json_body['image'])
                    filename = json_body['filename']
                    file_extension = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
                    return image_data, file_extension
                    
            except (json.JSONDecodeError, TypeError):
                pass
            
            if isinstance(body, str):
                try:
                    image_data = base64.b64decode(body)
                    file_extension = 'jpg'
                    return image_data, file_extension
                except Exception:
                    print("Failed to decode body as base64")
                    return None, None
            else:
                return body, 'jpg'
                
        except Exception as e:
            print(f"Error parsing image from event: {str(e)}")
            return None, None
