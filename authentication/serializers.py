"""Serializers for authentication endpoints."""

import re
from typing import Any, Dict

from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from authentication.models import User


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    
    Validates email, password complexity, and password confirmation.
    """
    
    first_name = serializers.CharField(max_length=100, required=True)
    last_name = serializers.CharField(max_length=100, required=True)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=255, required=True)
    password = serializers.CharField(min_length=8, write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    
    def validate_email(self, value: str) -> str:
        """
        Validate email format and uniqueness.
        
        Args:
            value: Email address
        
        Returns:
            Validated email
        
        Raises:
            serializers.ValidationError: If email is invalid or already exists
        """
        # Validate email format
        email_validator = EmailValidator()
        try:
            email_validator(value)
        except DjangoValidationError:
            raise serializers.ValidationError("Invalid email format")
        
        # Check uniqueness (case-insensitive)
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        return value.lower()
    
    def validate_password(self, value: str) -> str:
        """
        Validate password complexity.
        
        Requirements:
        - Minimum 8 characters
        - At least 1 uppercase letter
        - At least 1 lowercase letter
        - At least 1 number
        
        Args:
            value: Password
        
        Returns:
            Validated password
        
        Raises:
            serializers.ValidationError: If password doesn't meet requirements
        """
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Password must contain at least one number")
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate password confirmation matches password.
        
        Args:
            attrs: Validated attributes
        
        Returns:
            Validated attributes
        
        Raises:
            serializers.ValidationError: If passwords don't match
        """
        if attrs["password"] != attrs["password_confirmation"]:
            raise serializers.ValidationError({
                "password_confirmation": "Passwords do not match"
            })
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """
        Create a new user with hashed password.
        
        Args:
            validated_data: Validated user data
        
        Returns:
            Created User instance
        """
        # Remove password_confirmation from data
        validated_data.pop("password_confirmation")
        
        # Extract password
        password = validated_data.pop("password")
        
        # Create user
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (read-only).
    
    Used for returning user data in API responses.
    """
    
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "middle_name",
            "email",
            "is_active",
            "created_at",
            "updated_at",
            "last_login_at",
        ]
        read_only_fields = fields


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates email and password credentials.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, required=True)


class UpdateProfileSerializer(serializers.Serializer):
    """
    Serializer for updating user profile.
    
    All fields are optional.
    """
    
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    middle_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(max_length=255, required=False)
    
    def validate_email(self, value: str) -> str:
        """
        Validate email uniqueness (excluding current user).
        
        Args:
            value: Email address
        
        Returns:
            Validated email
        
        Raises:
            serializers.ValidationError: If email is already used by another user
        """
        user = self.context.get("user")
        
        # Check if email is already used by another user
        if User.objects.filter(email__iexact=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("User with this email already exists")
        
        return value.lower()
    
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        """
        Update user profile fields.
        
        Args:
            instance: User instance to update
            validated_data: Validated data
        
        Returns:
            Updated User instance
        """
        for field, value in validated_data.items():
            setattr(instance, field, value)
        
        instance.save()
        return instance
