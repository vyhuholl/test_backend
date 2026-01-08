"""Authorization models for RBAC system."""

import uuid

from django.db import models

from authentication.models import User


class Role(models.Model):
    """
    Role model for RBAC system.
    
    Defines user roles (admin, user, moderator, guest).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "roles"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of role."""
        return self.name


class BusinessElement(models.Model):
    """
    Business element model for RBAC system.
    
    Defines business resources (users, documents, projects, etc.).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "business_elements"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of business element."""
        return self.name


class AccessRoleRules(models.Model):
    """
    Access role rules model for RBAC system.
    
    Maps roles to business elements with granular permission flags.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="access_rules",
    )
    element = models.ForeignKey(
        BusinessElement,
        on_delete=models.CASCADE,
        related_name="access_rules",
    )
    read_permission = models.BooleanField(default=False)
    read_all_permission = models.BooleanField(default=False)
    create_permission = models.BooleanField(default=False)
    update_permission = models.BooleanField(default=False)
    update_all_permission = models.BooleanField(default=False)
    delete_permission = models.BooleanField(default=False)
    delete_all_permission = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "access_role_rules"
        ordering = ["role__name", "element__name"]
        unique_together = [["role", "element"]]
        indexes = [
            models.Index(fields=["role", "element"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of access rule."""
        return f"{self.role.name} - {self.element.name}"


class UserRole(models.Model):
    """
    User role junction model for RBAC system.
    
    Links users to their assigned roles with audit tracking.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_assignments_made",
    )
    
    class Meta:
        db_table = "user_roles"
        ordering = ["-assigned_at"]
        unique_together = [["user", "role"]]
        indexes = [
            models.Index(fields=["user", "role"]),
            models.Index(fields=["user"]),
        ]
    
    def __str__(self) -> str:
        """Return string representation of user role."""
        return f"{self.user.email} - {self.role.name}"
