from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
from application.jwt_service import JWTService
from application.image_service import ImageService
from repository.s3_repository import S3Repository
from domain.models import User, ImageUploadResponse, ImageDeleteResponse, ImageUploadRequest, ImageDeleteRequest
from config import Config

router = APIRouter(prefix="/api/v1", tags=["images"])
security = HTTPBearer()

# Initialize services
jwt_service = JWTService()
s3_repository = S3Repository()
image_service = ImageService(s3_repository)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """
    Dependency to get current user from JWT token
    """
    user = jwt_service.decode_token(credentials.credentials)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    return user


@router.post("/images/upload", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload an image file to S3
    
    Args:
        file: The image file to upload
        current_user: Current authenticated user
        
    Returns:
        ImageUploadResponse with upload details
    """
    try:
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="File must be an image"
            )
        
        file_extension = file.filename.split('.')[-1].lower() if file.filename and '.' in file.filename else 'jpg'
        
        if file_extension not in Config.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {', '.join(Config.ALLOWED_EXTENSIONS)}"
            )
        
        image_data = await file.read()
        
        if len(image_data) > Config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {Config.MAX_FILE_SIZE} bytes"
            )
        
        upload_request = ImageUploadRequest(
            user_id=current_user.id,
            image_data=image_data,
            content_type=file.content_type,
            file_extension=file_extension
        )
        
        response = image_service.upload_image(upload_request)
        
        if response.success:
            return ImageUploadResponse(
                success=True,
                image_url=response.image_url,
                message=response.message,
                user_id=current_user.id
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=response.message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.delete("/images/{image_name}", response_model=ImageDeleteResponse)
async def delete_image(
    image_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete an image from S3
    
    Args:
        image_name: Name of the image file to delete
        current_user: Current authenticated user
        
    Returns:
        ImageDeleteResponse with deletion status
    """
    try:
        delete_request = ImageDeleteRequest(
            user_id=current_user.id,
            image_name=image_name
        )
        
        response = image_service.delete_image(delete_request)
        
        if response.success:
            return ImageDeleteResponse(
                success=True,
                message=response.message,
                user_id=current_user.id
            )
        else:
            status_code = 404 if "not found" in response.message.lower() else 500
            raise HTTPException(
                status_code=status_code,
                detail=response.message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )


@router.get("/images/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "msai-image-uploader"}
