"""Tests for logout functionality."""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import TokenBlacklist, User
from core.jwt_utils import generate_jwt_token, hash_token


@pytest.fixture
def api_client() -> APIClient:
    """Provide API client for tests."""
    return APIClient()


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
class TestLogoutView:
    """Tests for LogoutView."""
    
    def test_successful_logout(self, api_client: APIClient, test_user: User) -> None:
        """Test successful logout returns 200."""
        token = generate_jwt_token(test_user)
        
        url = reverse("authentication:logout")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "message" in response.data["data"]
    
    def test_logout_blacklists_token(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test that logout adds token to blacklist."""
        token = generate_jwt_token(test_user)
        token_hash = hash_token(token)
        
        url = reverse("authentication:logout")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert TokenBlacklist.objects.filter(token_hash=token_hash).exists()
    
    def test_logout_without_authentication(self, api_client: APIClient) -> None:
        """Test logout without authentication returns 401."""
        url = reverse("authentication:logout")
        
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_blacklisted_token_rejected_on_subsequent_requests(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test that blacklisted token is rejected on subsequent requests."""
        token = generate_jwt_token(test_user)
        
        # First logout to blacklist token
        url = reverse("authentication:logout")
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to use the same token again (should fail)
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
