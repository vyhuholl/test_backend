"""Tests for JWT utility functions."""

import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import jwt
import pytest
from django.conf import settings

from core.jwt_utils import decode_jwt_token, generate_jwt_token, hash_token


class TestGenerateJWTToken:
    """Tests for generate_jwt_token function."""
    
    def test_generate_token_creates_valid_jwt(self) -> None:
        """Test that generate_jwt_token creates a valid JWT."""
        user = Mock()
        user.id = "550e8400-e29b-41d4-a716-446655440000"
        user.email = "test@example.com"
        
        token = generate_jwt_token(user)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verify token can be decoded
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
        assert "iat" in payload
        assert "exp" in payload
    
    def test_generate_token_includes_correct_claims(self) -> None:
        """Test that generated token includes all required claims."""
        user = Mock()
        user.id = "test-user-123"
        user.email = "user@example.com"
        
        token = generate_jwt_token(user)
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
        assert isinstance(payload["iat"], int)
        assert isinstance(payload["exp"], int)
        assert payload["exp"] > payload["iat"]
    
    def test_generate_token_expires_after_configured_lifetime(self) -> None:
        """Test that token expiration matches configured lifetime."""
        user = Mock()
        user.id = "test-id"
        user.email = "test@test.com"
        
        with patch("core.jwt_utils.datetime") as mock_datetime:
            now = datetime(2026, 1, 8, 12, 0, 0)
            mock_datetime.utcnow.return_value = now
            
            token = generate_jwt_token(user)
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            
            expected_exp = int((now + timedelta(seconds=settings.JWT_TOKEN_LIFETIME)).timestamp())
            assert payload["exp"] == expected_exp


class TestDecodeJWTToken:
    """Tests for decode_jwt_token function."""
    
    def test_decode_valid_token(self) -> None:
        """Test decoding a valid JWT token."""
        user = Mock()
        user.id = "test-user-456"
        user.email = "valid@example.com"
        
        token = generate_jwt_token(user)
        payload = decode_jwt_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
    
    def test_decode_expired_token_returns_none(self) -> None:
        """Test that expired tokens return None."""
        # Create a token that expired immediately
        past_time = datetime.utcnow() - timedelta(seconds=10)
        payload = {
            "sub": "test-user",
            "email": "test@test.com",
            "iat": int(past_time.timestamp()),
            "exp": int((past_time + timedelta(seconds=1)).timestamp()),
        }
        
        token = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        
        # Wait a moment to ensure token is expired
        result = decode_jwt_token(token)
        assert result is None
    
    def test_decode_invalid_signature_returns_none(self) -> None:
        """Test that tokens with invalid signature return None."""
        user = Mock()
        user.id = "test-user"
        user.email = "test@test.com"
        
        # Create token with different secret
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "iat": int(datetime.utcnow().timestamp()),
            "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
        }
        
        token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")
        result = decode_jwt_token(token)
        
        assert result is None
    
    def test_decode_malformed_token_returns_none(self) -> None:
        """Test that malformed tokens return None."""
        result = decode_jwt_token("not.a.valid.jwt.token")
        assert result is None


class TestHashToken:
    """Tests for hash_token function."""
    
    def test_hash_token_returns_sha256_hash(self) -> None:
        """Test that hash_token returns a SHA-256 hash."""
        token = "test.jwt.token"
        result = hash_token(token)
        
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 produces 64 hex characters
    
    def test_hash_token_is_deterministic(self) -> None:
        """Test that same token always produces same hash."""
        token = "same.token.every.time"
        hash1 = hash_token(token)
        hash2 = hash_token(token)
        
        assert hash1 == hash2
    
    def test_hash_token_different_for_different_tokens(self) -> None:
        """Test that different tokens produce different hashes."""
        token1 = "first.token"
        token2 = "second.token"
        
        hash1 = hash_token(token1)
        hash2 = hash_token(token2)
        
        assert hash1 != hash2
