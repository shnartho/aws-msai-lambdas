import os


class Config:
    """Configuration class for the image uploader service"""

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'secret_key')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'msai-images-bucket')
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff']
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 10 * 1024 * 1024))
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*')
    
    @classmethod
    def get_content_type(cls, file_extension: str) -> str:
        """Get content type based on file extension"""
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'bmp': 'image/bmp',
            'tiff': 'image/tiff',
            'svg': 'image/svg+xml'
        }
        return content_types.get(file_extension.lower(), 'application/octet-stream')
