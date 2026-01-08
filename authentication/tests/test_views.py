"""Tests for authentication views."""

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from authentication.models import User


@pytest.fixture
def api_client() -> APIClient:
    """Provide API client for tests."""
    return APIClient()


@pytest.mark.django_db
class TestRegisterView:
    """Tests for RegisterView."""
    
    def test_successful_registration(self, api_client: APIClient) -> None:
        """Test successful user registration returns 201."""
        url = reverse("authentication:register")
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "middle_name": "Sergeevich",
            "email": "ivan.petrov@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        assert "data" in response.data
        assert "meta" in response.data
        assert response.data["data"]["email"] == "ivan.petrov@example.com"
        assert response.data["data"]["first_name"] == "Ivan"
        assert response.data["data"]["last_name"] == "Petrov"
        assert response.data["data"]["middle_name"] == "Sergeevich"
        assert "password" not in response.data["data"]
        assert "password_hash" not in response.data["data"]
        
        # Verify user was created in database
        assert User.objects.filter(email="ivan.petrov@example.com").exists()
    
    def test_registration_with_duplicate_email(self, api_client: APIClient) -> None:
        """Test registration with existing email returns 400."""
        # Create existing user
        User.objects.create(
            first_name="Existing",
            last_name="User",
            email="existing@example.com",
            password_hash="hash",
        )
        
        url = reverse("authentication:register")
        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "existing@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
    
    def test_registration_with_invalid_email(self, api_client: APIClient) -> None:
        """Test registration with invalid email returns 400."""
        url = reverse("authentication:register")
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "not-an-email",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
    
    def test_registration_with_weak_password(self, api_client: APIClient) -> None:
        """Test registration with weak password returns 400."""
        url = reverse("authentication:register")
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "weak",
            "password_confirmation": "weak",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
    
    def test_registration_with_mismatched_passwords(self, api_client: APIClient) -> None:
        """Test registration with mismatched passwords returns 400."""
        url = reverse("authentication:register")
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "SecurePass123",
            "password_confirmation": "DifferentPass123",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
    
    def test_registration_without_required_fields(self, api_client: APIClient) -> None:
        """Test registration without required fields returns 400."""
        url = reverse("authentication:register")
        data = {
            "email": "test@example.com",
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
    
    def test_password_is_hashed_in_database(self, api_client: APIClient) -> None:
        """Test that password is hashed in database."""
        url = reverse("authentication:register")
        password = "SecurePass123"
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "hashtest@example.com",
            "password": password,
            "password_confirmation": password,
        }
        
        response = api_client.post(url, data, format="json")
        
        assert response.status_code == status.HTTP_201_CREATED
        
        user = User.objects.get(email="hashtest@example.com")
        assert user.password_hash != password
        assert user.password_hash.startswith("$2b$")  # bcrypt format
        assert user.check_password(password) is True
