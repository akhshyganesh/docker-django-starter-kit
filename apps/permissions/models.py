"""
RBAC and ABAC Models for fine-grained access control
"""
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from apps.core.models import AuditModel

User = get_user_model()


class Permission(AuditModel):
    """
    Custom permission model for fine-grained access control
    """
    
    PERMISSION_TYPES = [
        ('action', 'Action Permission'),
        ('resource', 'Resource Permission'),
        ('data', 'Data Permission'),
        ('system', 'System Permission'),
    ]
    
    name = models.CharField(max_length=255)
    codename = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES, default='action')
    
    # For resource-based permissions
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='custom_permissions'  # Avoid conflict with auth.Permission
    )
    
    # Additional attributes for ABAC
    attributes = models.JSONField(default=dict, blank=True)
    conditions = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        indexes = [
            models.Index(fields=['codename', 'is_active']),
            models.Index(fields=['permission_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.codename})"


class Role(AuditModel):
    """
    Role model for RBAC implementation
    """
    
    ROLE_TYPES = [
        ('system', 'System Role'),
        ('organizational', 'Organizational Role'),
        ('functional', 'Functional Role'),
        ('custom', 'Custom Role'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    role_type = models.CharField(max_length=20, choices=ROLE_TYPES, default='custom')
    
    # Role hierarchy
    parent_role = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_roles')
    
    # Role attributes for ABAC
    attributes = models.JSONField(default=dict, blank=True)
    
    # Role constraints
    max_users = models.PositiveIntegerField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        indexes = [
            models.Index(fields=['name', 'is_active']),
            models.Index(fields=['role_type']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_all_permissions(self):
        """Get all permissions for this role including inherited ones"""
        permissions = set()
        
        # Direct permissions
        role_perms = RolePermission.objects.filter(
            role=self,
            is_active=True
        ).select_related('permission')
        
        for role_perm in role_perms:
            permissions.add(role_perm.permission)
        
        # Inherited permissions from parent roles
        if self.parent_role:
            parent_perms = self.parent_role.get_all_permissions()
            permissions.update(parent_perms)
        
        return permissions
    
    @property
    def user_count(self):
        """Get number of users assigned to this role"""
        return self.users.filter(is_active=True).count()


class RolePermission(AuditModel):
    """
    Many-to-many relationship between roles and permissions with additional attributes
    """
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='role_permissions')
    
    # ABAC attributes
    conditions = models.JSONField(default=dict, blank=True)
    constraints = models.JSONField(default=dict, blank=True)
    
    # Time-based access
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'role_permissions'
        unique_together = ['role', 'permission']
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        indexes = [
            models.Index(fields=['role', 'permission', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(AuditModel):
    """
    Many-to-many relationship between users and roles with additional attributes
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='users')
    
    # Role assignment context
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles'
    )
    
    # Time-based assignment
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Assignment attributes
    attributes = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'user_roles'
        unique_together = ['user', 'role']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        indexes = [
            models.Index(fields=['user', 'role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


class UserPermission(AuditModel):
    """
    Direct user permissions (bypassing roles)
    """
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='custom_user_permissions'  # Avoid conflict with built-in user_permissions
    )
    permission = models.ForeignKey(
        Permission, 
        on_delete=models.CASCADE, 
        related_name='custom_user_permissions'
    )
    
    # Permission grant/deny
    granted = models.BooleanField(default=True)
    
    # ABAC attributes
    conditions = models.JSONField(default=dict, blank=True)
    constraints = models.JSONField(default=dict, blank=True)
    
    # Time-based access
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    # Assignment context
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_permissions'
    )
    reason = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_permissions'
        unique_together = ['user', 'permission']
        verbose_name = 'User Permission'
        verbose_name_plural = 'User Permissions'
        indexes = [
            models.Index(fields=['user', 'permission', 'is_active']),
        ]
    
    def __str__(self):
        grant_deny = "Grant" if self.granted else "Deny"
        return f"{self.user.email} - {self.permission.name} ({grant_deny})"


class ResourcePermission(AuditModel):
    """
    Resource-based permissions for ABAC
    """
    
    PERMISSION_TYPES = [
        ('read', 'Read'),
        ('write', 'Write'),
        ('delete', 'Delete'),
        ('execute', 'Execute'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resource_permissions')
    permission_type = models.CharField(max_length=20, choices=PERMISSION_TYPES)
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # ABAC attributes
    conditions = models.JSONField(default=dict, blank=True)
    attributes = models.JSONField(default=dict, blank=True)
    
    # Time-based access
    valid_from = models.DateTimeField(null=True, blank=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'resource_permissions'
        unique_together = ['user', 'permission_type', 'content_type', 'object_id']
        verbose_name = 'Resource Permission'
        verbose_name_plural = 'Resource Permissions'
        indexes = [
            models.Index(fields=['user', 'content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.permission_type} on {self.content_object}"


class PolicyRule(AuditModel):
    """
    ABAC policy rules
    """
    
    RULE_TYPES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
        ('conditional', 'Conditional'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES, default='allow')
    
    # Policy rule definition
    subject_attributes = models.JSONField(default=dict, blank=True)  # User attributes
    resource_attributes = models.JSONField(default=dict, blank=True)  # Resource attributes
    action_attributes = models.JSONField(default=dict, blank=True)  # Action attributes
    environment_attributes = models.JSONField(default=dict, blank=True)  # Environment attributes
    
    # Conditions
    conditions = models.JSONField(default=dict, blank=True)
    
    # Priority for rule evaluation
    priority = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'policy_rules'
        verbose_name = 'Policy Rule'
        verbose_name_plural = 'Policy Rules'
        ordering = ['-priority', 'name']
        indexes = [
            models.Index(fields=['rule_type', 'priority']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.rule_type})"
    
    def evaluate(self, user, resource, action, environment=None):
        """
        Evaluate this policy rule against the given context
        """
        # This is a simplified evaluation - in production, you'd want
        # a more sophisticated policy engine
        try:
            # Check subject attributes
            if not self._match_attributes(user, self.subject_attributes):
                return False
            
            # Check resource attributes
            if not self._match_attributes(resource, self.resource_attributes):
                return False
            
            # Check action attributes
            if not self._match_attributes(action, self.action_attributes):
                return False
            
            # Check environment attributes
            if environment and not self._match_attributes(environment, self.environment_attributes):
                return False
            
            # Evaluate conditions
            if self.conditions:
                return self._evaluate_conditions(user, resource, action, environment)
            
            return True
            
        except Exception:
            # In case of evaluation error, default to deny
            return False
    
    def _match_attributes(self, obj, required_attributes):
        """Check if object matches required attributes"""
        if not required_attributes:
            return True
        
        for attr_name, attr_value in required_attributes.items():
            if hasattr(obj, attr_name):
                obj_value = getattr(obj, attr_name)
                if obj_value != attr_value:
                    return False
            else:
                return False
        
        return True
    
    def _evaluate_conditions(self, user, resource, action, environment):
        """Evaluate complex conditions"""
        # This would implement a condition evaluation engine
        # For now, returning True as a placeholder
        return True


class AuditLog(models.Model):
    """
    Audit log for permission-related activities
    """
    
    ACTION_TYPES = [
        ('permission_granted', 'Permission Granted'),
        ('permission_denied', 'Permission Denied'),
        ('permission_revoked', 'Permission Revoked'),
        ('role_assigned', 'Role Assigned'),
        ('role_revoked', 'Role Revoked'),
        ('policy_applied', 'Policy Applied'),
        ('access_denied', 'Access Denied'),
        ('access_granted', 'Access Granted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    resource = models.CharField(max_length=255, blank=True)
    permission = models.CharField(max_length=255, blank=True)
    
    # Request context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=255, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Additional context
    details = models.JSONField(default=dict, blank=True)
    success = models.BooleanField(default=True)
    reason = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['success', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email if self.user else 'Unknown'} - {self.action_type} - {self.timestamp}"
