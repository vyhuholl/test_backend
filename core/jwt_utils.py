"""JWT token generation and validation utilities."""

import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from django.conf import settings


def generate_jwt_token(user: Any) -> str:
    """
    Generate a JWT token for the given user.
    
    Args:
        user: User model instance
    
    Returns:
        JWT token string
    """
    now = datetime.utcnow()
    expiration = now + timedelta(seconds=settings.JWT_TOKEN_LIFETIME)
    
    payload = {
        "sub": str(user.id),  # Subject (user ID)
        "email": user.email,
        "iat": int(now.timestamp()),  # Issued at
        "exp": int(expiration.timestamp()),  # Expiration
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return token


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload dict, or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return None
    except jwt.InvalidTokenError:
        # Token is invalid (bad signature, malformed, etc.)
        return None


def hash_token(token: str) -> str:
    """
    Create a SHA-256 hash of a token for storage in blacklist.
    
    Args:
        token: JWT token string
    
    Returns:
        SHA-256 hash of the token as hex string
    """
    return hashlib.sha256(token.encode()).hexdigest()
