"""Tests for custom exception handlers."""

from unittest.mock import Mock

import pytest
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response

from core.constants import (
    AUTHENTICATION_REQUIRED,
    INSUFFICIENT_PERMISSIONS,
    INTERNAL_ERROR,
    NOT_FOUND,
    RATE_LIMIT_EXCEEDED,
    VALIDATION_ERROR,
)
from core.exceptions import custom_exception_handler, format_validation_errors


class TestCustomExceptionHandler:
    """Tests for custom_exception_handler function."""
    
    def test_validation_error_handling(self) -> None:
        """Test handling of ValidationError."""
        exc = exceptions.ValidationError({"email": ["Invalid email format"]})
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data
        assert response.data["error"]["code"] == VALIDATION_ERROR
        assert len(response.data["error"]["details"]) > 0
    
    def test_authentication_failed_handling(self) -> None:
        """Test handling of AuthenticationFailed."""
        exc = exceptions.AuthenticationFailed("Invalid token")
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["error"]["code"] == AUTHENTICATION_REQUIRED
    
    def test_not_authenticated_handling(self) -> None:
        """Test handling of NotAuthenticated."""
        exc = exceptions.NotAuthenticated()
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["error"]["code"] == AUTHENTICATION_REQUIRED
    
    def test_permission_denied_handling(self) -> None:
        """Test handling of PermissionDenied."""
        exc = exceptions.PermissionDenied()
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["error"]["code"] == INSUFFICIENT_PERMISSIONS
    
    def test_not_found_handling(self) -> None:
        """Test handling of NotFound."""
        exc = exceptions.NotFound()
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == NOT_FOUND
    
    def test_throttled_handling(self) -> None:
        """Test handling of Throttled (rate limiting)."""
        exc = exceptions.Throttled(wait=60)
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data["error"]["code"] == RATE_LIMIT_EXCEEDED
        assert "60" in response.data["error"]["message"]
    
    def test_django_http404_handling(self) -> None:
        """Test handling of Django's Http404."""
        exc = Http404()
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["error"]["code"] == NOT_FOUND
    
    def test_unhandled_exception(self) -> None:
        """Test handling of unhandled exceptions."""
        exc = ValueError("Some error")
        context = {}
        response = custom_exception_handler(exc, context)
        
        assert response is not None
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert response.data["error"]["code"] == INTERNAL_ERROR


class TestFormatValidationErrors:
    """Tests for format_validation_errors function."""
    
    def test_format_dict_errors(self) -> None:
        """Test formatting dict-based validation errors."""
        errors = {
            "email": ["Invalid format"],
            "password": ["Too short", "No uppercase"],
        }
        result = format_validation_errors(errors)
        
        assert len(result) == 3
        assert {"field": "email", "message": "Invalid format"} in result
        assert {"field": "password", "message": "Too short"} in result
        assert {"field": "password", "message": "No uppercase"} in result
    
    def test_format_list_errors(self) -> None:
        """Test formatting list-based validation errors."""
        errors = ["Error 1", "Error 2"]
        result = format_validation_errors(errors)
        
        assert len(result) == 2
        assert all(d["field"] == "non_field_errors" for d in result)
    
    def test_format_string_error(self) -> None:
        """Test formatting string validation error."""
        errors = "Single error message"
        result = format_validation_errors(errors)
        
        assert len(result) == 1
        assert result[0]["field"] == "non_field_errors"
        assert result[0]["message"] == errors
