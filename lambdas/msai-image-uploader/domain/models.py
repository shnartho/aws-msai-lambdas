from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    """User model extracted from JWT token"""
    id: str
    username: Optional[str] = None
    email: Optional[str] = None

@dataclass
class ImageUploadResponse:
    """Image upload response model"""
    success: bool
    image_url: str
    message: str
    user_id: str

@dataclass
class ImageDeleteResponse:
    """Image delete response model"""
    success: bool
    message: str
    user_id: str

@dataclass
class ErrorResponse:
    """Error response model"""
    error: str
    detail: Optional[str] = None


@dataclass
class ImageUploadRequest:
    """Image upload request model"""
    user_id: str
    image_data: bytes
    content_type: str
    file_extension: str


@dataclass
class ImageDeleteRequest:
    """Image delete request model"""
    user_id: str
    image_name: str
