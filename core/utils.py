"""Core utility functions for standardized API responses."""

from datetime import datetime
from typing import Any, Dict, Optional


def response_success(
    data: Any,
    meta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: The response data payload
        meta: Optional metadata dictionary (timestamp, total_count, etc.)
    
    Returns:
        Dict containing data and meta fields
    """
    response = {
        "data": data,
        "meta": {
            "timestamp": datetime.now().isoformat(),
        },
    }
    
    if meta:
        response["meta"].update(meta)
    
    return response


def response_error(
    code: str,
    message: str,
    details: Optional[list] = None,
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        code: Error code constant (e.g., 'VALIDATION_ERROR')
        message: Human-readable error message
        details: Optional list of field-specific errors
    
    Returns:
        Dict containing error field with code, message, and details
    """
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        }
    }
