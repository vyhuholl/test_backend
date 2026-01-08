"""Tests for authentication models."""

import pytest
from django.db import IntegrityError

from authentication.models import User


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model."""
    
    def test_create_user(self) -> None:
        """Test creating a basic user."""
        user = User.objects.create(
            first_name="Ivan",
            last_name="Petrov",
            email="ivan.petrov@example.com",
            password_hash="dummy_hash",
        )
        
        assert user.id is not None
        assert user.first_name == "Ivan"
        assert user.last_name == "Petrov"
        assert user.email == "ivan.petrov@example.com"
        assert user.is_active is True
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_user_email_must_be_unique(self) -> None:
        """Test that user email must be unique."""
        User.objects.create(
            first_name="User",
            last_name="One",
            email="same@example.com",
            password_hash="hash1",
        )
        
        with pytest.raises(IntegrityError):
            User.objects.create(
                first_name="User",
                last_name="Two",
                email="same@example.com",
                password_hash="hash2",
            )
    
    def test_user_str_returns_email(self) -> None:
        """Test __str__ method returns email."""
        user = User.objects.create(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hash",
        )
        
        assert str(user) == "test@example.com"
    
    def test_set_password_hashes_password(self) -> None:
        """Test set_password hashes password with bcrypt."""
        user = User(
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        
        password = "SecurePass123"
        user.set_password(password)
        
        assert user.password_hash is not None
        assert user.password_hash != password
        assert user.password_hash.startswith("$2b$")  # bcrypt hash marker
    
    def test_check_password_validates_correct_password(self) -> None:
        """Test check_password returns True for correct password."""
        user = User(
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        
        password = "SecurePass123"
        user.set_password(password)
        
        assert user.check_password(password) is True
    
    def test_check_password_rejects_incorrect_password(self) -> None:
        """Test check_password returns False for incorrect password."""
        user = User(
            first_name="Test",
            last_name="User",
            email="test@example.com",
        )
        
        user.set_password("CorrectPassword123")
        
        assert user.check_password("WrongPassword123") is False
    
    def test_user_with_middle_name(self) -> None:
        """Test creating user with middle name."""
        user = User.objects.create(
            first_name="Ivan",
            last_name="Petrov",
            middle_name="Sergeevich",
            email="ivan.s.petrov@example.com",
            password_hash="hash",
        )
        
        assert user.middle_name == "Sergeevich"
    
    def test_user_without_middle_name(self) -> None:
        """Test creating user without middle name."""
        user = User.objects.create(
            first_name="Ivan",
            last_name="Petrov",
            email="ivan.petrov@example.com",
            password_hash="hash",
        )
        
        assert user.middle_name is None
