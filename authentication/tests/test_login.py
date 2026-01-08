"""Tests for login functionality."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User


@pytest.fixture
def api_client() -> APIClient:
    """Provide API client for tests."""
    return APIClient()


@pytest.fixture
def test_user(db: Any) -> User:
    """Create a test user for login tests."""
    user = User(
        first_name="Test",
        last_name="User",
        email="test@example.com",
    )
    user.set_password("TestPass123")
    user.save()
    return user


@pytest.mark.django_db
class TestLoginView:
    """Tests for LoginView."""
    
    def test_successful_login(self, api_client: APIClient, test_user: User) -> None:
        """Test successful login returns 200 with token."""
        url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "token" in response.data["data"]
        assert "token_type" in response.data["data"]
        assert response.data["data"]["token_type"] == "Bearer"
        assert "expires_in" in response.data["data"]
        assert "user" in response.data["data"]
        assert response.data["data"]["user"]["email"] == "test@example.com"
        assert "password" not in response.data["data"]["user"]
        
        # Verify token is a valid JWT
        token = response.data["data"]["token"]
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_login_with_invalid_email(self, api_client: APIClient, test_user: User) -> None:
        """Test login with non-existent email returns 401."""
        url = reverse("authentication:login")
        data = {
            "email": "nonexistent@example.com",
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data
        assert response.data["error"]["code"] == "INVALID_CREDENTIALS"
    
    def test_login_with_wrong_password(self, api_client: APIClient, test_user: User) -> None:
        """Test login with wrong password returns 401."""
        url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
            "password": "WrongPassword123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data
        assert response.data["error"]["code"] == "INVALID_CREDENTIALS"
    
    def test_login_with_inactive_account(self, api_client: APIClient, test_user: User) -> None:
        """Test login with inactive account returns 403."""
        # Deactivate user
        test_user.is_active = False
        test_user.save()
        
        url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "error" in response.data
        assert response.data["error"]["code"] == "ACCOUNT_INACTIVE"
    
    def test_login_case_insensitive_email(self, api_client: APIClient, test_user: User) -> None:
        """Test login works with case-insensitive email."""
        url = reverse("authentication:login")
        data = {
            "email": "TEST@EXAMPLE.COM",
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data["data"]
    
    def test_login_updates_last_login_at(self, api_client: APIClient, test_user: User) -> None:
        """Test that login updates last_login_at timestamp."""
        assert test_user.last_login_at is None
        
        url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh user from database
        test_user.refresh_from_db()
        assert test_user.last_login_at is not None
    
    def test_login_without_email(self, api_client: APIClient) -> None:
        """Test login without email returns 400."""
        url = reverse("authentication:login")
        data = {
            "password": "TestPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_without_password(self, api_client: APIClient) -> None:
        """Test login without password returns 400."""
        url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


from typing import Any  # Import at top of file
