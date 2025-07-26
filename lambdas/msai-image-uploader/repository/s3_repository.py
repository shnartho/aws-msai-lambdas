import boto3
import os
from datetime import datetime
from typing import Optional
from botocore.exceptions import ClientError
from config import Config


class S3Repository:
    """Repository for S3 operations"""
    
    def __init__(self, bucket_name: Optional[str] = None):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name or Config.S3_BUCKET_NAME
    
    def upload_image(self, user_id: str, image_data: bytes, file_extension: str) -> tuple[bool, str, str]:
        """
        Upload image to S3
        
        Args:
            user_id: User ID to create directory structure
            image_data: Image binary data
            file_extension: File extension (e.g., 'jpg', 'png')
            
        Returns:
            Tuple of (success, image_url, message)
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            image_name = f"{timestamp}.{file_extension}"
            
            s3_key = f"{user_id}/{image_name}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=image_data,
                ContentType=Config.get_content_type(file_extension)
            )            
            image_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            return True, image_url, f"Image uploaded successfully as {image_name}"
            
        except ClientError as e:
            error_message = f"Failed to upload image: {str(e)}"
            print(error_message)
            return False, "", error_message
        except Exception as e:
            error_message = f"Unexpected error during upload: {str(e)}"
            print(error_message)
            return False, "", error_message
    
    def delete_image(self, user_id: str, image_name: str) -> tuple[bool, str]:
        """
        Delete image from S3
        
        Args:
            user_id: User ID for directory structure
            image_name: Name of the image file to delete
            
        Returns:
            Tuple of (success, message)
        """
        try:
            s3_key = f"{user_id}/{image_name}"
            
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    return False, f"Image {image_name} not found"
                raise e            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return True, f"Image {image_name} deleted successfully"
            
        except ClientError as e:
            error_message = f"Failed to delete image: {str(e)}"
            print(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"Unexpected error during deletion: {str(e)}"
            print(error_message)
            return False, error_message
