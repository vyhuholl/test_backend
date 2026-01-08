"""Custom authentication backends for Django REST Framework."""

from typing import Any, Optional, Tuple

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from authentication.models import User
from core.jwt_utils import decode_jwt_token


class JWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication backend.
    
    Validates JWT tokens from Authorization header.
    """
    
    def authenticate(self, request: Request) -> Optional[Tuple[Any, Any]]:
        """
        Authenticate the request using JWT token from Authorization header.
        
        Args:
            request: The HTTP request
        
        Returns:
            Tuple of (user, token) if authenticated, None otherwise
        
        Raises:
            AuthenticationFailed: If token is invalid or user not found
        """
        # Get Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return None
        
        # Check for Bearer scheme
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        
        token = parts[1]
        
        # Decode and validate token
        payload = decode_jwt_token(token)
        
        if payload is None:
            raise AuthenticationFailed("Invalid or expired token")
        
        # Get user ID from payload
        user_id = payload.get("sub")
        
        if not user_id:
            raise AuthenticationFailed("Invalid token payload")
        
        # Check if token is blacklisted
        from authentication.utils import is_token_blacklisted
        from core.jwt_utils import hash_token
        
        token_hash = hash_token(token)
        if is_token_blacklisted(token_hash):
            raise AuthenticationFailed("Token has been revoked")
        
        # Get user from database
        try:
            user = User.objects.get(id=user_id, is_active=True)
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found or inactive")
        
        return (user, token)
    
    def authenticate_header(self, request: Request) -> str:
        """
        Return the WWW-Authenticate header value.
        
        Args:
            request: The HTTP request
        
        Returns:
            Authentication scheme name
        """
        return "Bearer"
