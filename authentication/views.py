"""Views for authentication endpoints."""

from datetime import datetime

from django.conf import settings
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied, Throttled
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from authentication.serializers import (
    LoginSerializer,
    RegisterSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)
from authentication.utils import blacklist_token
from core.constants import ACCOUNT_INACTIVE, INVALID_CREDENTIALS, RATE_LIMIT_EXCEEDED
from core.jwt_utils import generate_jwt_token
from core.utils import response_error, response_success


def ratelimit_handler(request: Request, exception: Exception) -> Response:
    """Custom handler for rate limit exceeded."""
    return Response(
        response_error(
            code=RATE_LIMIT_EXCEEDED,
            message="Rate limit exceeded. Please try again later.",
        ),
        status=status.HTTP_429_TOO_MANY_REQUESTS,
    )


class RegisterView(APIView):
    """
    API view for user registration.
    
    POST /api/auth/register - Register a new user
    """
    
    permission_classes = []  # Allow unauthenticated access
    authentication_classes = []  # No authentication required
    
    def post(self, request: Request) -> Response:
        """
        Register a new user.
        
        Args:
            request: HTTP request containing user registration data
        
        Returns:
            Response with created user data (201) or validation errors (400)
        """
        serializer = RegisterSerializer(data=request.data)
        
        if not serializer.is_valid():
            # Validation errors will be handled by custom exception handler
            serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Return user data
        user_serializer = UserSerializer(user)
        return Response(
            response_success(user_serializer.data),
            status=status.HTTP_201_CREATED,
        )


@method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True), name='dispatch')
class LoginView(APIView):
    """
    API view for user login.
    
    POST /api/auth/login - Authenticate and get JWT token
    Rate limited to 5 attempts per minute per IP.
    """
    
    permission_classes = []  # Allow unauthenticated access
    authentication_classes = []  # No authentication required
    
    def post(self, request: Request) -> Response:
        """
        Authenticate user and return JWT token.
        
        Args:
            request: HTTP request containing email and password
        
        Returns:
            Response with JWT token and user data (200) or error (401/403)
        """
        serializer = LoginSerializer(data=request.data)
        
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        
        # Get user by email (case-insensitive)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise AuthenticationFailed(
                detail=response_error(
                    code=INVALID_CREDENTIALS,
                    message="Invalid email or password",
                )
            )
        
        # Check if account is active
        if not user.is_active:
            raise PermissionDenied(
                detail=response_error(
                    code=ACCOUNT_INACTIVE,
                    message="Account has been deactivated",
                )
            )
        
        # Verify password
        if not user.check_password(password):
            raise AuthenticationFailed(
                detail=response_error(
                    code=INVALID_CREDENTIALS,
                    message="Invalid email or password",
                )
            )
        
        # Update last login timestamp
        user.last_login_at = datetime.now()
        user.save(update_fields=["last_login_at"])
        
        # Generate JWT token
        token = generate_jwt_token(user)
        
        # Prepare response data
        user_serializer = UserSerializer(user)
        data = {
            "token": token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_TOKEN_LIFETIME,
            "user": user_serializer.data,
        }
        
        return Response(
            response_success(data),
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    API view for user logout.
    
    POST /api/auth/logout - Invalidate JWT token (requires authentication)
    """
    
    def post(self, request: Request) -> Response:
        """
        Logout user by blacklisting current JWT token.
        
        Args:
            request: HTTP request with authenticated user
        
        Returns:
            Response with success message (200) or error (401)
        """
        # Get the current token from request
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed(
                detail=response_error(
                    code="AUTHENTICATION_REQUIRED",
                    message="Authentication token required",
                )
            )
        
        token = auth_header.split()[1]
        
        # Blacklist the token
        blacklist_token(token, request.user)
        
        return Response(
            response_success({"message": "Successfully logged out"}),
            status=status.HTTP_200_OK,
        )


class ProfileView(APIView):
    """
    API view for user profile management.
    
    GET /api/auth/profile - Get current user profile
    PATCH /api/auth/profile - Update current user profile
    """
    
    def get(self, request: Request) -> Response:
        """
        Get authenticated user's profile.
        
        Args:
            request: HTTP request with authenticated user
        
        Returns:
            Response with user profile data (200)
        """
        serializer = UserSerializer(request.user)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )
    
    def patch(self, request: Request) -> Response:
        """
        Update authenticated user's profile.
        
        Args:
            request: HTTP request with update data
        
        Returns:
            Response with updated user data (200) or validation errors (400)
        """
        serializer = UpdateProfileSerializer(
            data=request.data,
            context={"user": request.user},
        )
        
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        # Update user
        user = serializer.update(request.user, serializer.validated_data)
        
        # Return updated user data
        user_serializer = UserSerializer(user)
        return Response(
            response_success(user_serializer.data),
            status=status.HTTP_200_OK,
        )


class DeleteAccountView(APIView):
    """
    API view for soft deleting user account.
    
    DELETE /api/auth/profile - Soft delete account (requires authentication)
    """
    
    def delete(self, request: Request) -> Response:
        """
        Soft delete user account by setting is_active to False.
        
        Args:
            request: HTTP request with authenticated user
        
        Returns:
            Response with success message (200)
        """
        # Get the current token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split()[1]
            # Blacklist the current token
            blacklist_token(token, request.user)
        
        # Soft delete user
        request.user.is_active = False
        request.user.save(update_fields=["is_active"])
        
        return Response(
            response_success({"message": "Account successfully deleted"}),
            status=status.HTTP_200_OK,
        )
