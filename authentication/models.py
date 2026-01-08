"""Authentication models including User and TokenBlacklist."""

import uuid
from datetime import datetime
from typing import Optional

import bcrypt
from django.db import models


class User(models.Model):
    """
    Custom user model for authentication.
    
    Uses bcrypt for password hashing and UUID for primary key.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    password_hash = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["is_active"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of user."""
        return self.email
    
    def set_password(self, password: str) -> None:
        """
        Hash password using bcrypt with 12 rounds.
        
        Args:
            password: Plain text password
        """
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode(), salt)
        self.password_hash = hashed.decode()
    
    def check_password(self, password: str) -> bool:
        """
        Verify password against stored hash using bcrypt.
        
        Args:
            password: Plain text password to verify
        
        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())


class TokenBlacklist(models.Model):
    """
    Store blacklisted JWT tokens for logout functionality.
    
    Tokens are stored as SHA-256 hashes for security.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blacklisted_tokens",
    )
    blacklisted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    
    class Meta:
        db_table = "token_blacklist"
        ordering = ["-blacklisted_at"]
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["expires_at"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of blacklisted token."""
        return f"Blacklisted token for {self.user.email} at {self.blacklisted_at}"
