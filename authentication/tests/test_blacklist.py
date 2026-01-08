"""Tests for token blacklist functionality."""

from datetime import datetime, timedelta
from typing import Any

import pytest

from authentication.models import TokenBlacklist, User
from authentication.utils import blacklist_token, is_token_blacklisted
from core.jwt_utils import generate_jwt_token, hash_token


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
class TestBlacklistToken:
    """Tests for blacklist_token function."""
    
    def test_blacklist_token_creates_entry(self, test_user: User) -> None:
        """Test that blacklisting a token creates a database entry."""
        token = generate_jwt_token(test_user)
        
        blacklist_entry = blacklist_token(token, test_user)
        
        assert blacklist_entry.id is not None
        assert blacklist_entry.user == test_user
        assert blacklist_entry.token_hash is not None
        assert blacklist_entry.expires_at is not None
        assert blacklist_entry.blacklisted_at is not None
    
    def test_blacklist_token_stores_hash(self, test_user: User) -> None:
        """Test that token is stored as hash, not plain text."""
        token = generate_jwt_token(test_user)
        expected_hash = hash_token(token)
        
        blacklist_entry = blacklist_token(token, test_user)
        
        assert blacklist_entry.token_hash == expected_hash
        assert blacklist_entry.token_hash != token
    
    def test_blacklist_token_sets_expiration(self, test_user: User) -> None:
        """Test that expiration is set from token payload."""
        token = generate_jwt_token(test_user)
        
        blacklist_entry = blacklist_token(token, test_user)
        
        # expires_at should be in the future (24 hours)
        assert blacklist_entry.expires_at > datetime.now()


@pytest.mark.django_db
class TestIsTokenBlacklisted:
    """Tests for is_token_blacklisted function."""
    
    def test_is_token_blacklisted_returns_true_for_blacklisted(
        self, test_user: User
    ) -> None:
        """Test that function returns True for blacklisted token."""
        token = generate_jwt_token(test_user)
        token_hash = hash_token(token)
        
        # Blacklist the token
        TokenBlacklist.objects.create(
            token_hash=token_hash,
            user=test_user,
            expires_at=datetime.now() + timedelta(hours=24),
        )
        
        assert is_token_blacklisted(token_hash) is True
    
    def test_is_token_blacklisted_returns_false_for_not_blacklisted(
        self, test_user: User
    ) -> None:
        """Test that function returns False for non-blacklisted token."""
        token = generate_jwt_token(test_user)
        token_hash = hash_token(token)
        
        assert is_token_blacklisted(token_hash) is False
