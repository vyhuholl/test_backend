"""Tests for profile management."""

from typing import Any

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User
from core.jwt_utils import generate_jwt_token


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
        middle_name="Middle",
        email="test@example.com",
    )
    user.set_password("TestPass123")
    user.save()
    return user


@pytest.mark.django_db
class TestProfileView:
    """Tests for ProfileView."""
    
    def test_get_profile_authenticated(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test GET profile returns user data for authenticated user."""
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:profile")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "data" in response.data
        assert response.data["data"]["email"] == "test@example.com"
        assert response.data["data"]["first_name"] == "Test"
        assert response.data["data"]["last_name"] == "User"
        assert response.data["data"]["middle_name"] == "Middle"
        assert "password" not in response.data["data"]
        assert "password_hash" not in response.data["data"]
    
    def test_get_profile_unauthenticated(self, api_client: APIClient) -> None:
        """Test GET profile returns 401 for unauthenticated request."""
        url = reverse("authentication:profile")
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_patch_profile_update_name(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test PATCH profile updates user name."""
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:profile")
        data = {
            "first_name": "Updated",
            "last_name": "Name",
        }
        response = api_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["first_name"] == "Updated"
        assert response.data["data"]["last_name"] == "Name"
        
        # Verify in database
        test_user.refresh_from_db()
        assert test_user.first_name == "Updated"
        assert test_user.last_name == "Name"
    
    def test_patch_profile_update_email(
        self, api_client: APIClient, test_user: User
    ) -> None:
        """Test PATCH profile updates email."""
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:profile")
        data = {"email": "newemail@example.com"}
        response = api_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == "newemail@example.com"
        
        # Verify in database
        test_user.refresh_from_db()
        assert test_user.email == "newemail@example.com"
    
    def test_patch_profile_duplicate_email(
        self, api_client: APIClient, test_user: User, db: Any
    ) -> None:
        """Test PATCH profile with existing email returns 400."""
        # Create another user
        other_user = User.objects.create(
            first_name="Other",
            last_name="User",
            email="other@example.com",
            password_hash="hash",
        )
        
        token = generate_jwt_token(test_user)
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        
        url = reverse("authentication:profile")
        data = {"email": "other@example.com"}
        response = api_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_patch_profile_unauthenticated(self, api_client: APIClient) -> None:
        """Test PATCH profile returns 401 for unauthenticated request."""
        url = reverse("authentication:profile")
        data = {"first_name": "Updated"}
        response = api_client.patch(url, data, format="json")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
