"""Tests for core utility functions."""

from datetime import datetime

import pytest

from core.utils import response_error, response_success


class TestResponseSuccess:
    """Tests for response_success function."""
    
    def test_response_success_with_data_only(self) -> None:
        """Test response_success with data only."""
        data = {"id": 1, "name": "Test"}
        result = response_success(data)
        
        assert "data" in result
        assert "meta" in result
        assert result["data"] == data
        assert "timestamp" in result["meta"]
        # Verify timestamp is ISO format
        datetime.fromisoformat(result["meta"]["timestamp"])
    
    def test_response_success_with_meta(self) -> None:
        """Test response_success with custom meta."""
        data = [{"id": 1}, {"id": 2}]
        meta = {"total_count": 2, "page": 1}
        result = response_success(data, meta=meta)
        
        assert result["data"] == data
        assert result["meta"]["total_count"] == 2
        assert result["meta"]["page"] == 1
        assert "timestamp" in result["meta"]
    
    def test_response_success_with_empty_data(self) -> None:
        """Test response_success with empty data."""
        result = response_success([])
        
        assert result["data"] == []
        assert "meta" in result
        assert "timestamp" in result["meta"]


class TestResponseError:
    """Tests for response_error function."""
    
    def test_response_error_basic(self) -> None:
        """Test response_error with basic parameters."""
        code = "VALIDATION_ERROR"
        message = "Invalid input"
        result = response_error(code, message)
        
        assert "error" in result
        assert result["error"]["code"] == code
        assert result["error"]["message"] == message
        assert result["error"]["details"] == []
    
    def test_response_error_with_details(self) -> None:
        """Test response_error with field details."""
        code = "VALIDATION_ERROR"
        message = "Validation failed"
        details = [
            {"field": "email", "message": "Invalid email format"},
            {"field": "password", "message": "Too short"},
        ]
        result = response_error(code, message, details)
        
        assert result["error"]["code"] == code
        assert result["error"]["message"] == message
        assert result["error"]["details"] == details
    
    def test_response_error_with_none_details(self) -> None:
        """Test response_error with None details defaults to empty list."""
        result = response_error("TEST_ERROR", "Test message", None)
        
        assert result["error"]["details"] == []
