"""
Serializers for permissions management
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Permission, Role, RolePermission, UserRole, UserPermission, AuditLog

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model
    """
    
    class Meta:
        model = Permission
        fields = [
            'id', 'name', 'codename', 'description', 'permission_type',
            'content_type', 'attributes', 'conditions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for RolePermission model
    """
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'permission', 'permission_id', 'conditions',
            'constraints', 'valid_from', 'valid_until', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model
    """
    permissions = serializers.SerializerMethodField()
    user_count = serializers.ReadOnlyField()
    role_permissions = RolePermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'role_type', 'parent_role',
            'attributes', 'max_users', 'expires_at', 'user_count',
            'permissions', 'role_permissions', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_count', 'created_at', 'updated_at']
    
    def get_permissions(self, obj):
        """Get all permissions for this role"""
        permissions = obj.get_all_permissions()
        return [
            {
                'id': perm.id,
                'name': perm.name,
                'codename': perm.codename,
                'permission_type': perm.permission_type
            }
            for perm in permissions
        ]


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model
    """
    user = serializers.SerializerMethodField()
    role = RoleSerializer(read_only=True)
    role_id = serializers.UUIDField(write_only=True)
    assigned_by = serializers.SerializerMethodField()
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'role', 'role_id', 'assigned_by',
            'valid_from', 'valid_until', 'attributes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        """Get user information"""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.full_name,
            'user_type': obj.user.user_type
        }
    
    def get_assigned_by(self, obj):
        """Get assigned by user information"""
        if obj.assigned_by:
            return {
                'id': obj.assigned_by.id,
                'email': obj.assigned_by.email,
                'full_name': obj.assigned_by.full_name
            }
        return None


class UserPermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for UserPermission model
    """
    user = serializers.SerializerMethodField()
    permission = PermissionSerializer(read_only=True)
    permission_id = serializers.UUIDField(write_only=True)
    assigned_by = serializers.SerializerMethodField()
    
    class Meta:
        model = UserPermission
        fields = [
            'id', 'user', 'permission', 'permission_id', 'granted',
            'conditions', 'constraints', 'valid_from', 'valid_until',
            'assigned_by', 'reason', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user(self, obj):
        """Get user information"""
        return {
            'id': obj.user.id,
            'email': obj.user.email,
            'full_name': obj.user.full_name
        }
    
    def get_assigned_by(self, obj):
        """Get assigned by user information"""
        if obj.assigned_by:
            return {
                'id': obj.assigned_by.id,
                'email': obj.assigned_by.email,
                'full_name': obj.assigned_by.full_name
            }
        return None


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Serializer for AuditLog model
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action_type', 'resource', 'permission',
            'ip_address', 'user_agent', 'request_path', 'request_method',
            'details', 'success', 'reason', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_user(self, obj):
        """Get user information"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'full_name': obj.user.full_name
            }
        return None
