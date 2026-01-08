"""Utility functions for authentication."""

from datetime import datetime, timedelta
from typing import Any

from django.conf import settings

from authentication.models import TokenBlacklist
from core.jwt_utils import decode_jwt_token, hash_token


def blacklist_token(token: str, user: Any) -> TokenBlacklist:
    """
    Add a token to the blacklist.
    
    Args:
        token: JWT token to blacklist
        user: User who owns the token
    
    Returns:
        Created TokenBlacklist instance
    """
    # Hash the token
    token_hash = hash_token(token)
    
    # Decode token to get expiration
    payload = decode_jwt_token(token)
    
    if payload:
        expires_at = datetime.fromtimestamp(payload["exp"])
    else:
        # If token is already invalid, set expiration to current time + token lifetime
        expires_at = datetime.now() + timedelta(seconds=settings.JWT_TOKEN_LIFETIME)
    
    # Create blacklist entry
    blacklist_entry = TokenBlacklist.objects.create(
        token_hash=token_hash,
        user=user,
        expires_at=expires_at,
    )
    
    return blacklist_entry


def is_token_blacklisted(token_hash: str) -> bool:
    """
    Check if a token hash is in the blacklist.
    
    Args:
        token_hash: SHA-256 hash of the token
    
    Returns:
        True if token is blacklisted, False otherwise
    """
    return TokenBlacklist.objects.filter(token_hash=token_hash).exists()
