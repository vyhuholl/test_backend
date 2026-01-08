"""Tests for authentication serializers."""

import pytest
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.serializers import RegisterSerializer


@pytest.mark.django_db
class TestRegisterSerializer:
    """Tests for RegisterSerializer."""
    
    def test_valid_registration_data(self) -> None:
        """Test serializer accepts valid registration data."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "middle_name": "Sergeevich",
            "email": "ivan@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
    
    def test_email_validation_rejects_invalid_format(self) -> None:
        """Test email validation rejects invalid email format."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "invalid-email",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
    
    def test_email_validation_rejects_duplicate_email(self) -> None:
        """Test email validation rejects already registered email."""
        # Create existing user
        User.objects.create(
            first_name="Existing",
            last_name="User",
            email="existing@example.com",
            password_hash="hash",
        )
        
        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "existing@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
    
    def test_email_validation_case_insensitive(self) -> None:
        """Test email validation is case-insensitive."""
        User.objects.create(
            first_name="Existing",
            last_name="User",
            email="test@example.com",
            password_hash="hash",
        )
        
        data = {
            "first_name": "New",
            "last_name": "User",
            "email": "TEST@EXAMPLE.COM",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors
    
    def test_password_validation_minimum_length(self) -> None:
        """Test password must be at least 8 characters."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "Short1",
            "password_confirmation": "Short1",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
    
    def test_password_validation_requires_uppercase(self) -> None:
        """Test password must contain at least one uppercase letter."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "nouppercase123",
            "password_confirmation": "nouppercase123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
    
    def test_password_validation_requires_lowercase(self) -> None:
        """Test password must contain at least one lowercase letter."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "NOLOWERCASE123",
            "password_confirmation": "NOLOWERCASE123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
    
    def test_password_validation_requires_number(self) -> None:
        """Test password must contain at least one number."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "NoNumbersHere",
            "password_confirmation": "NoNumbersHere",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
    
    def test_password_confirmation_must_match(self) -> None:
        """Test password confirmation must match password."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "ivan@example.com",
            "password": "SecurePass123",
            "password_confirmation": "DifferentPass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password_confirmation" in serializer.errors
    
    def test_create_user_with_valid_data(self) -> None:
        """Test creating user with valid data."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "middle_name": "Sergeevich",
            "email": "new.user@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        
        assert user.id is not None
        assert user.first_name == "Ivan"
        assert user.last_name == "Petrov"
        assert user.middle_name == "Sergeevich"
        assert user.email == "new.user@example.com"
        assert user.password_hash is not None
        assert user.password_hash != "SecurePass123"
        assert user.is_active is True
    
    def test_create_user_without_middle_name(self) -> None:
        """Test creating user without middle name."""
        data = {
            "first_name": "Ivan",
            "last_name": "Petrov",
            "email": "no.middle@example.com",
            "password": "SecurePass123",
            "password_confirmation": "SecurePass123",
        }
        
        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        
        assert user.middle_name in [None, ""]
