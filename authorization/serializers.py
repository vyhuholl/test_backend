"""Serializers for authorization endpoints."""

from typing import Any, Dict

from rest_framework import serializers

from authorization.models import AccessRoleRules, BusinessElement, Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreateRoleSerializer(serializers.Serializer):
    """Serializer for creating a new role."""
    
    name = serializers.CharField(max_length=50, required=True)
    description = serializers.CharField(max_length=255, required=True)
    
    def validate_name(self, value: str) -> str:
        """Validate role name is unique and lowercase."""
        value = value.lower()
        if Role.objects.filter(name=value).exists():
            raise serializers.ValidationError("Role with this name already exists")
        return value
    
    def create(self, validated_data: Dict[str, Any]) -> Role:
        """Create a new role."""
        return Role.objects.create(**validated_data)


class BusinessElementSerializer(serializers.ModelSerializer):
    """Serializer for BusinessElement model."""
    
    class Meta:
        model = BusinessElement
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = fields


class AccessRuleSerializer(serializers.ModelSerializer):
    """Serializer for AccessRoleRules with nested role and element."""
    
    role = RoleSerializer(read_only=True)
    element = BusinessElementSerializer(read_only=True)
    
    class Meta:
        model = AccessRoleRules
        fields = [
            'id',
            'role',
            'element',
            'read_permission',
            'read_all_permission',
            'create_permission',
            'update_permission',
            'update_all_permission',
            'delete_permission',
            'delete_all_permission',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class CreateAccessRuleSerializer(serializers.Serializer):
    """Serializer for creating access rules."""
    
    role_id = serializers.UUIDField(required=True)
    element_id = serializers.UUIDField(required=True)
    read_permission = serializers.BooleanField(default=False)
    read_all_permission = serializers.BooleanField(default=False)
    create_permission = serializers.BooleanField(default=False)
    update_permission = serializers.BooleanField(default=False)
    update_all_permission = serializers.BooleanField(default=False)
    delete_permission = serializers.BooleanField(default=False)
    delete_all_permission = serializers.BooleanField(default=False)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate role and element exist and rule doesn't already exist."""
        role_id = attrs['role_id']
        element_id = attrs['element_id']
        
        # Check role exists
        try:
            Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role_id": "Role not found"})
        
        # Check element exists
        try:
            BusinessElement.objects.get(id=element_id)
        except BusinessElement.DoesNotExist:
            raise serializers.ValidationError({"element_id": "Business element not found"})
        
        # Check if rule already exists
        if AccessRoleRules.objects.filter(role_id=role_id, element_id=element_id).exists():
            raise serializers.ValidationError("Access rule for this role and element already exists")
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> AccessRoleRules:
        """Create a new access rule."""
        return AccessRoleRules.objects.create(**validated_data)


class UpdateAccessRuleSerializer(serializers.Serializer):
    """Serializer for updating access rule permissions."""
    
    read_permission = serializers.BooleanField(required=False)
    read_all_permission = serializers.BooleanField(required=False)
    create_permission = serializers.BooleanField(required=False)
    update_permission = serializers.BooleanField(required=False)
    update_all_permission = serializers.BooleanField(required=False)
    delete_permission = serializers.BooleanField(required=False)
    delete_all_permission = serializers.BooleanField(required=False)
    
    def update(self, instance: AccessRoleRules, validated_data: Dict[str, Any]) -> AccessRoleRules:
        """Update access rule permissions."""
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for assigning a role to a user."""
    
    role_id = serializers.UUIDField(required=True)
    
    def validate_role_id(self, value: str) -> str:
        """Validate role exists."""
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role not found")
        return value


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole with nested role."""
    
    role = RoleSerializer(read_only=True)
    
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'assigned_at', 'assigned_by']
        read_only_fields = fields
