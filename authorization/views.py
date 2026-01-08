"""Views for authorization admin endpoints."""

from rest_framework import status
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User
from authorization.models import AccessRoleRules, BusinessElement, Role, UserRole
from authorization.serializers import (
    AccessRuleSerializer,
    AssignRoleSerializer,
    BusinessElementSerializer,
    CreateAccessRuleSerializer,
    CreateRoleSerializer,
    RoleSerializer,
    UpdateAccessRuleSerializer,
    UserRoleSerializer,
)
from core.permissions import IsAdmin
from core.utils import response_success


class RoleListCreateView(ListCreateAPIView):
    """
    List all roles or create a new role.
    
    GET /api/admin/roles - List all roles
    POST /api/admin/roles - Create new role
    """
    
    permission_classes = [IsAdmin]
    queryset = Role.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on method."""
        if self.request.method == 'POST':
            return CreateRoleSerializer
        return RoleSerializer
    
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all roles."""
        roles = self.get_queryset()
        serializer = RoleSerializer(roles, many=True)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new role."""
        serializer = CreateRoleSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        role = serializer.save()
        role_serializer = RoleSerializer(role)
        return Response(
            response_success(role_serializer.data),
            status=status.HTTP_201_CREATED,
        )


class RoleDetailView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a role.
    
    GET /api/admin/roles/{id} - Get role details
    PATCH /api/admin/roles/{id} - Update role description
    DELETE /api/admin/roles/{id} - Delete role
    """
    
    permission_classes = [IsAdmin]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """Get role details."""
        role = self.get_object()
        serializer = RoleSerializer(role)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )
    
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """Update role description (name is immutable)."""
        role = self.get_object()
        
        # Only allow updating description
        if 'description' in request.data:
            role.description = request.data['description']
            role.save()
        
        serializer = RoleSerializer(role)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )
    
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """Delete role (only if not assigned to any users)."""
        role = self.get_object()
        
        # Check if role is assigned to any users
        if UserRole.objects.filter(role=role).exists():
            return Response(
                {"error": {"code": "ROLE_IN_USE", "message": "Cannot delete role that is assigned to users"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        role.delete()
        return Response(
            response_success({"message": "Role deleted successfully"}),
            status=status.HTTP_200_OK,
        )


class BusinessElementListView(ListAPIView):
    """
    List all business elements.
    
    GET /api/admin/business-elements - List all business elements
    """
    
    permission_classes = [IsAdmin]
    queryset = BusinessElement.objects.all()
    serializer_class = BusinessElementSerializer
    
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List all business elements."""
        elements = self.get_queryset()
        serializer = BusinessElementSerializer(elements, many=True)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )


class AccessRuleListCreateView(ListCreateAPIView):
    """
    List all access rules or create a new access rule.
    
    GET /api/admin/access-rules - List access rules (with optional filtering)
    POST /api/admin/access-rules - Create new access rule
    """
    
    permission_classes = [IsAdmin]
    
    def get_queryset(self):
        """Get access rules with optional filtering."""
        queryset = AccessRoleRules.objects.select_related('role', 'element').all()
        
        # Optional filtering by role or element
        role_id = self.request.query_params.get('role_id')
        element_id = self.request.query_params.get('element_id')
        
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        if element_id:
            queryset = queryset.filter(element_id=element_id)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on method."""
        if self.request.method == 'POST':
            return CreateAccessRuleSerializer
        return AccessRuleSerializer
    
    def list(self, request: Request, *args, **kwargs) -> Response:
        """List access rules."""
        rules = self.get_queryset()
        serializer = AccessRuleSerializer(rules, many=True)
        return Response(
            response_success(serializer.data),
            status=status.HTTP_200_OK,
        )
    
    def create(self, request: Request, *args, **kwargs) -> Response:
        """Create a new access rule."""
        serializer = CreateAccessRuleSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        rule = serializer.save()
        rule_serializer = AccessRuleSerializer(rule)
        return Response(
            response_success(rule_serializer.data),
            status=status.HTTP_201_CREATED,
        )


class AccessRuleUpdateView(APIView):
    """
    Update access rule permissions.
    
    PATCH /api/admin/access-rules/{id} - Update permission flags
    """
    
    permission_classes = [IsAdmin]
    
    def patch(self, request: Request, pk: str) -> Response:
        """Update access rule permissions."""
        try:
            rule = AccessRoleRules.objects.select_related('role', 'element').get(pk=pk)
        except AccessRoleRules.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Access rule not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        serializer = UpdateAccessRuleSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        rule = serializer.update(rule, serializer.validated_data)
        rule_serializer = AccessRuleSerializer(rule)
        return Response(
            response_success(rule_serializer.data),
            status=status.HTTP_200_OK,
        )


class AssignRoleView(APIView):
    """
    Assign a role to a user.
    
    POST /api/admin/users/{user_id}/roles - Assign role to user
    """
    
    permission_classes = [IsAdmin]
    
    def post(self, request: Request, user_id: str) -> Response:
        """Assign role to user."""
        # Get user
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Validate role
        serializer = AssignRoleSerializer(data=request.data)
        if not serializer.is_valid():
            serializer.is_valid(raise_exception=True)
        
        role_id = serializer.validated_data['role_id']
        
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Role not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Create user role assignment
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'assigned_by': request.user},
        )
        
        if not created:
            return Response(
                {"error": {"code": "ALREADY_ASSIGNED", "message": "User already has this role"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Get all user roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        serializer = UserRoleSerializer(user_roles, many=True)
        
        return Response(
            response_success({
                "user_id": str(user.id),
                "roles": serializer.data,
            }),
            status=status.HTTP_200_OK,
        )


class RemoveRoleView(APIView):
    """
    Remove a role from a user.
    
    DELETE /api/admin/users/{user_id}/roles/{role_id} - Remove role from user
    """
    
    permission_classes = [IsAdmin]
    
    def delete(self, request: Request, user_id: str, role_id: str) -> Response:
        """Remove role from user."""
        # Get user
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Get role
        try:
            role = Role.objects.get(pk=role_id)
        except Role.DoesNotExist:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "Role not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Delete user role assignment
        deleted_count, _ = UserRole.objects.filter(user=user, role=role).delete()
        
        if deleted_count == 0:
            return Response(
                {"error": {"code": "NOT_FOUND", "message": "User does not have this role"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        return Response(
            response_success({"message": "Role removed successfully"}),
            status=status.HTTP_200_OK,
        )
