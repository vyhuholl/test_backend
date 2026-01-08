"""Custom permission classes for Django REST Framework."""

from typing import Any

from django.db.models import Q
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import View


class IsAdmin(BasePermission):
    """
    Permission class to check if user has admin role.
    """
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has admin role.
        
        Args:
            request: The HTTP request
            view: The view being accessed
        
        Returns:
            True if user has admin role, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Check if user has admin role
        return request.user.user_roles.filter(role__name='admin').exists()


class RBACPermission(BasePermission):
    """
    Permission class for role-based access control.
    
    Checks if user has required permission for a specific business element and action.
    """
    
    # Map HTTP methods to permission flags
    METHOD_PERMISSION_MAP = {
        'GET': 'read_all_permission',  # For list views
        'POST': 'create_permission',
        'PUT': 'update_all_permission',
        'PATCH': 'update_all_permission',
        'DELETE': 'delete_all_permission',
    }
    
    def has_permission(self, request: Request, view: View) -> bool:
        """
        Check if user has required permission for the resource action.
        
        Args:
            request: The HTTP request
            view: The view being accessed
        
        Returns:
            True if user has required permission, False otherwise
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get element name from view (must be set on view as 'rbac_element')
        element_name = getattr(view, 'rbac_element', None)
        if not element_name:
            # If no element specified, deny by default
            return False
        
        # Get required permission based on HTTP method
        method = request.method
        permission_field = self.METHOD_PERMISSION_MAP.get(method)
        
        if not permission_field:
            return False
        
        # Check if user has any role with the required permission
        # Use select_related and prefetch_related for query optimization
        from authorization.models import AccessRoleRules
        
        user_role_ids = request.user.user_roles.values_list('role_id', flat=True)
        
        has_permission = AccessRoleRules.objects.filter(
            role_id__in=user_role_ids,
            element__name=element_name,
            **{permission_field: True}
        ).exists()
        
        return has_permission
