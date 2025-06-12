"""
Admin configuration for Permissions app
"""
from django.contrib import admin
from .models import (
    Permission, Role, RolePermission, UserRole, UserPermission,
    ResourcePermission, PolicyRule, AuditLog
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Admin for permissions"""
    
    list_display = [
        'name', 'codename', 'permission_type', 'content_type', 'is_active'
    ]
    
    list_filter = ['permission_type', 'is_active', 'created_at']
    
    search_fields = ['name', 'codename', 'description']
    
    fields = [
        'name', 'codename', 'description', 'permission_type',
        'content_type', 'attributes', 'conditions', 'is_active'
    ]
    
    readonly_fields = ['created_at', 'updated_at']


class RolePermissionInline(admin.TabularInline):
    """Inline for role permissions"""
    model = RolePermission
    extra = 0
    fields = ['permission', 'conditions', 'valid_from', 'valid_until', 'is_active']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """Admin for roles"""
    
    inlines = [RolePermissionInline]
    
    list_display = [
        'name', 'role_type', 'parent_role', 'user_count', 'is_active'
    ]
    
    list_filter = ['role_type', 'is_active', 'created_at']
    
    search_fields = ['name', 'description']
    
    fields = [
        'name', 'description', 'role_type', 'parent_role',
        'attributes', 'max_users', 'expires_at', 'is_active'
    ]
    
    readonly_fields = ['user_count', 'created_at', 'updated_at']


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for user roles"""
    
    list_display = [
        'user', 'role', 'assigned_by', 'valid_from', 'valid_until', 'is_active'
    ]
    
    list_filter = ['role', 'is_active', 'created_at']
    
    search_fields = ['user__email', 'role__name']
    
    fields = [
        'user', 'role', 'assigned_by', 'valid_from', 'valid_until',
        'attributes', 'is_active'
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPermission)
class UserPermissionAdmin(admin.ModelAdmin):
    """Admin for user permissions"""
    
    list_display = [
        'user', 'permission', 'granted', 'assigned_by',
        'valid_from', 'valid_until', 'is_active'
    ]
    
    list_filter = ['granted', 'permission', 'is_active', 'created_at']
    
    search_fields = ['user__email', 'permission__name']
    
    fields = [
        'user', 'permission', 'granted', 'conditions', 'constraints',
        'valid_from', 'valid_until', 'assigned_by', 'reason', 'is_active'
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PolicyRule)
class PolicyRuleAdmin(admin.ModelAdmin):
    """Admin for policy rules"""
    
    list_display = ['name', 'rule_type', 'priority', 'is_active']
    
    list_filter = ['rule_type', 'is_active', 'created_at']
    
    search_fields = ['name', 'description']
    
    fields = [
        'name', 'description', 'rule_type', 'priority',
        'subject_attributes', 'resource_attributes',
        'action_attributes', 'environment_attributes',
        'conditions', 'is_active'
    ]
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for audit logs"""
    
    list_display = [
        'user', 'action_type', 'resource', 'success',
        'ip_address', 'timestamp'
    ]
    
    list_filter = ['action_type', 'success', 'timestamp']
    
    search_fields = ['user__email', 'resource', 'permission', 'ip_address']
    
    fields = [
        'user', 'action_type', 'resource', 'permission',
        'ip_address', 'user_agent', 'request_path', 'request_method',
        'details', 'success', 'reason', 'timestamp'
    ]
    
    readonly_fields = ['timestamp']
    
    date_hierarchy = 'timestamp'
