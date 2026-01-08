"""URL patterns for authorization admin endpoints."""

from django.urls import path

from authorization.views import (
    AccessRuleListCreateView,
    AccessRuleUpdateView,
    AssignRoleView,
    BusinessElementListView,
    RemoveRoleView,
    RoleDetailView,
    RoleListCreateView,
)


app_name = "authorization"

urlpatterns = [
    # Role management
    path("roles", RoleListCreateView.as_view(), name="role_list_create"),
    path("roles/<uuid:pk>", RoleDetailView.as_view(), name="role_detail"),
    
    # Business elements
    path("business-elements", BusinessElementListView.as_view(), name="business_element_list"),
    
    # Access rules
    path("access-rules", AccessRuleListCreateView.as_view(), name="access_rule_list_create"),
    path("access-rules/<uuid:pk>", AccessRuleUpdateView.as_view(), name="access_rule_update"),
    
    # User role assignment
    path("users/<uuid:user_id>/roles", AssignRoleView.as_view(), name="assign_role"),
    path("users/<uuid:user_id>/roles/<uuid:role_id>", RemoveRoleView.as_view(), name="remove_role"),
]
