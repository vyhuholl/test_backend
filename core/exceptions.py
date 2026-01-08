"""Custom exception handlers for Django REST Framework."""

from typing import Any, Dict, Optional

from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.constants import (
    AUTHENTICATION_REQUIRED,
    INSUFFICIENT_PERMISSIONS,
    INTERNAL_ERROR,
    NOT_FOUND,
    RATE_LIMIT_EXCEEDED,
    VALIDATION_ERROR,
)
from core.utils import response_error


def custom_exception_handler(
    exc: Exception, context: Dict[str, Any]
) -> Optional[Response]:
    """
    Custom exception handler that returns standardized error responses.
    
    Args:
        exc: The exception instance
        context: Context information about where the exception occurred
    
    Returns:
        Response object with standardized error format, or None if not handled
    """
    # Call DRF's default exception handler first to get the standard error response
    response = drf_exception_handler(exc, context)
    
    if response is not None:
        # DRF handled the exception, format it consistently
        error_data = format_error_response(exc, response)
        response.data = error_data
        return response
    
    # Handle Django's built-in exceptions
    if isinstance(exc, Http404):
        error_data = response_error(
            code=NOT_FOUND,
            message="The requested resource was not found.",
            details=[],
        )
        return Response(error_data, status=status.HTTP_404_NOT_FOUND)
    
    if isinstance(exc, PermissionDenied):
        error_data = response_error(
            code=INSUFFICIENT_PERMISSIONS,
            message="You do not have permission to perform this action.",
            details=[],
        )
        return Response(error_data, status=status.HTTP_403_FORBIDDEN)
    
    # For unhandled exceptions, return a generic error (don't expose details)
    error_data = response_error(
        code=INTERNAL_ERROR,
        message="An internal server error occurred.",
        details=[],
    )
    return Response(error_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def format_error_response(exc: Exception, response: Response) -> Dict[str, Any]:
    """
    Format DRF exception responses to match our standard error format.
    
    Args:
        exc: The exception instance
        response: The DRF response object
    
    Returns:
        Dict with standardized error format
    """
    # Determine error code based on exception type
    if isinstance(exc, exceptions.ValidationError):
        code = VALIDATION_ERROR
        message = "Validation error occurred."
        details = format_validation_errors(response.data)
    elif isinstance(exc, exceptions.AuthenticationFailed):
        code = AUTHENTICATION_REQUIRED
        message = str(exc) if str(exc) else "Authentication failed."
        details = []
    elif isinstance(exc, exceptions.NotAuthenticated):
        code = AUTHENTICATION_REQUIRED
        message = "Valid authentication token required."
        details = []
    elif isinstance(exc, exceptions.PermissionDenied):
        code = INSUFFICIENT_PERMISSIONS
        message = str(exc) if str(exc) else "Permission denied."
        details = []
    elif isinstance(exc, exceptions.NotFound):
        code = NOT_FOUND
        message = str(exc) if str(exc) else "Resource not found."
        details = []
    elif isinstance(exc, exceptions.Throttled):
        code = RATE_LIMIT_EXCEEDED
        wait_time = getattr(exc, 'wait', None)
        message = f"Rate limit exceeded. Please try again in {wait_time} seconds." if wait_time else "Rate limit exceeded."
        details = []
    else:
        code = INTERNAL_ERROR
        message = "An error occurred while processing your request."
        details = []
    
    return response_error(code=code, message=message, details=details)


def format_validation_errors(errors: Any) -> list:
    """
    Format DRF validation errors into our standard details format.
    
    Args:
        errors: Validation errors from DRF (dict or list)
    
    Returns:
        List of dicts with field and message keys
    """
    details = []
    
    if isinstance(errors, dict):
        for field, messages in errors.items():
            if isinstance(messages, list):
                for message in messages:
                    details.append({
                        "field": field,
                        "message": str(message),
                    })
            else:
                details.append({
                    "field": field,
                    "message": str(messages),
                })
    elif isinstance(errors, list):
        for message in errors:
            details.append({
                "field": "non_field_errors",
                "message": str(message),
            })
    else:
        details.append({
            "field": "non_field_errors",
            "message": str(errors),
        })
    
    return details
