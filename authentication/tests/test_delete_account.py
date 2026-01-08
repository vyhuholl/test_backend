"""Tests for account deletion."""

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
class TestDeleteAccountView:
    """Tests for DeleteAccountView."""
    
    def test_delete_account_successful(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test successful account deletion returns 200."""
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:delete_account")
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert "message" in response.data["data"]
    
    def test_delete_account_sets_is_active_false(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test that delete account sets is_active to False."""
        assert test_user.is_active is True
        
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:delete_account")
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deactivated
        test_user.refresh_from_db()
        assert test_user.is_active is False
    
    def test_delete_account_blacklists_token(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test that delete account blacklists current token."""
        token = generate_jwt_token(test_user)
        token_hash = hash_token(token)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:delete_account")
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert TokenBlacklist.objects.filter(token_hash=token_hash).exists()
    
    def test_inactive_user_cannot_login(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test that user cannot login after account deletion."""
        # Delete account
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        delete_url = reverse("authentication:delete_account")
        response = api_client.delete(delete_url)
        assert response.status_code == status.HTTP_200_OK
        
        # Try to login
        login_url = reverse("authentication:login")
        data = {
            "email": "test@example.com",
            "password": "TestPass123",
        }
        response = api_client.post(login_url, data, format="json")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "error" in response.data
        assert response.data["error"]["code"] == "ACCOUNT_INACTIVE"
    
    def test_delete_account_unauthenticated(self, api_client: APIClient) -> None:
        """Test delete account returns 401 for unauthenticated request."""
        url = reverse("authentication:delete_account")
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
