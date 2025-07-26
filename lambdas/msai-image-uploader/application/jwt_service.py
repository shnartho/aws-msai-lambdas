import jwt
from typing import Optional
from domain.models import User
from config import Config


class JWTService:
    """Service for handling JWT token operations"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or Config.JWT_SECRET_KEY
    
    def decode_token(self, token: str) -> Optional[User]:
        """
        Decode JWT token and return User object
        
        Args:
            token: JWT token string
            
        Returns:
            User object if token is valid, None otherwise
        """
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            user_id = payload.get('id') or payload.get('user_id') or payload.get('sub')
            username = payload.get('username')
            email = payload.get('email')
            
            if not user_id:
                return None
                
            return User(
                id=str(user_id),
                username=username,
                email=email
            )
            
        except jwt.ExpiredSignatureError:
            print("Token has expired")
            return None
        except jwt.InvalidTokenError:
            print("Invalid token")
            return None
        except Exception as e:
            print(f"Error decoding token: {str(e)}")
            return None
