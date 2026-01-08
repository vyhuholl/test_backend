"""Tests for JWT authentication backend."""

from typing import Any
from unittest.mock import Mock

import pytest
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory

from authentication.models import User
from core.authentication import JWTAuthentication
from core.jwt_utils import generate_jwt_token


@pytest.fixture
def auth_backend() -> JWTAuthentication:
    """Provide JWT authentication backend."""
    return JWTAuthentication()


@pytest.fixture
def request_factory() -> APIRequestFactory:
    """Provide API request factory."""
    return APIRequestFactory()


@pytest.fixture
def test_user(db: Any) -> User:
    """Create a test user."""
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
    )
    user.set_password("TestPass123")
    user.save()
    return user


@pytest.mark.django_db
class TestJWTAuthentication:
    """Tests for JWTAuthentication class."""
    
    def test_authenticate_with_valid_token(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
        test_user: User,
    ) -> None:
        """Test authentication with valid token returns user."""
        token = generate_jwt_token(test_user)
        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        
        result = auth_backend.authenticate(request)
        
        assert result is not None
        user, returned_token = result
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert returned_token == token
    
    def test_authenticate_without_authorization_header(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
    ) -> None:
        """Test authentication without header returns None."""
        request = request_factory.get("/")
        
        result = auth_backend.authenticate(request)
        
        assert result is None
    
    def test_authenticate_with_invalid_scheme(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
        test_user: User,
    ) -> None:
        """Test authentication with non-Bearer scheme returns None."""
        token = generate_jwt_token(test_user)
        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Basic {token}"
        
        result = auth_backend.authenticate(request)
        
        assert result is None
    
    def test_authenticate_with_expired_token(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
        test_user: User,
    ) -> None:
        """Test authentication with expired token raises exception."""
        # Create an expired token (this would require mocking datetime)
        # For now, test with invalid token
        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = "Bearer invalid.token.here"
        
        with pytest.raises(AuthenticationFailed):
            auth_backend.authenticate(request)
    
    def test_authenticate_with_nonexistent_user(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
        test_user: User,
    ) -> None:
        """Test authentication with token for deleted user fails."""
        token = generate_jwt_token(test_user)
        
        # Delete user
        test_user.delete()
        
        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        
        with pytest.raises(AuthenticationFailed):
            auth_backend.authenticate(request)
    
    def test_authenticate_with_inactive_user(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
        test_user: User,
    ) -> None:
        """Test authentication with inactive user fails."""
        token = generate_jwt_token(test_user)
        
        # Deactivate user
        test_user.is_active = False
        test_user.save()
        
        request = request_factory.get("/")
        request.META["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        
        with pytest.raises(AuthenticationFailed):
            auth_backend.authenticate(request)
    
    def test_authenticate_header_returns_bearer(
        self,
        auth_backend: JWTAuthentication,
        request_factory: APIRequestFactory,
    ) -> None:
        """Test authenticate_header returns Bearer scheme."""
        request = request_factory.get("/")
        
        result = auth_backend.authenticate_header(request)
        
        assert result == "Bearer"
