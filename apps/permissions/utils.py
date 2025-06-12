"""
Utility functions for permissions management
"""
import logging
from django.contrib.auth import get_user_model
from .models import Permission, Role, RolePermission

logger = logging.getLogger(__name__)
User = get_user_model()


def create_default_permissions():
    """
    Create default permissions for the application
    """
    default_permissions = [
        # User management permissions
        {
            'name': 'View User',
            'codename': 'view_user',
            'description': 'Can view user information',
            'permission_type': 'resource'
        },
        {
            'name': 'Add User',
            'codename': 'add_user',
            'description': 'Can create new users',
            'permission_type': 'action'
        },
        {
            'name': 'Change User',
            'codename': 'change_user',
            'description': 'Can modify user information',
            'permission_type': 'action'
        },
        {
            'name': 'Delete User',
            'codename': 'delete_user',
            'description': 'Can delete users',
            'permission_type': 'action'
        },
        {
            'name': 'Change User Role',
            'codename': 'change_user_role',
            'description': 'Can assign/revoke user roles',
            'permission_type': 'action'
        },
        {
            'name': 'Change User Status',
            'codename': 'change_user_status',
            'description': 'Can activate/deactivate/lock users',
            'permission_type': 'action'
        },
        
        # Role management permissions
        {
            'name': 'View Role',
            'codename': 'view_role',
            'description': 'Can view role information',
            'permission_type': 'resource'
        },
        {
            'name': 'Add Role',
            'codename': 'add_role',
            'description': 'Can create new roles',
            'permission_type': 'action'
        },
        {
            'name': 'Change Role',
            'codename': 'change_role',
            'description': 'Can modify role information',
            'permission_type': 'action'
        },
        {
            'name': 'Delete Role',
            'codename': 'delete_role',
            'description': 'Can delete roles',
            'permission_type': 'action'
        },
        
        # Permission management permissions
        {
            'name': 'View Permission',
            'codename': 'view_permission',
            'description': 'Can view permission information',
            'permission_type': 'resource'
        },
        {
            'name': 'Add Permission',
            'codename': 'add_permission',
            'description': 'Can create new permissions',
            'permission_type': 'action'
        },
        {
            'name': 'Change Permission',
            'codename': 'change_permission',
            'description': 'Can modify permission information',
            'permission_type': 'action'
        },
        {
            'name': 'Delete Permission',
            'codename': 'delete_permission',
            'description': 'Can delete permissions',
            'permission_type': 'action'
        },
        
        # System permissions
        {
            'name': 'View System Settings',
            'codename': 'view_system_settings',
            'description': 'Can view system configuration',
            'permission_type': 'system'
        },
        {
            'name': 'Change System Settings',
            'codename': 'change_system_settings',
            'description': 'Can modify system configuration',
            'permission_type': 'system'
        },
        {
            'name': 'View Audit Logs',
            'codename': 'view_audit_logs',
            'description': 'Can view audit logs',
            'permission_type': 'system'
        },
        {
            'name': 'Export Data',
            'codename': 'export_data',
            'description': 'Can export system data',
            'permission_type': 'system'
        },
        
        # API permissions
        {
            'name': 'API Access',
            'codename': 'api_access',
            'description': 'Can access API endpoints',
            'permission_type': 'system'
        },
        {
            'name': 'API Admin',
            'codename': 'api_admin',
            'description': 'Can access admin API endpoints',
            'permission_type': 'system'
        },
    ]
    
    created_permissions = []
    
    for perm_data in default_permissions:
        permission, created = Permission.objects.get_or_create(
            codename=perm_data['codename'],
            defaults=perm_data
        )
        
        if created:
            created_permissions.append(permission)
            logger.info(f"Created permission: {permission.name}")
    
    # Create default roles
    create_default_roles(created_permissions)
    
    return created_permissions


def create_default_roles():
    """
    Create default roles with appropriate permissions
    """
    default_roles = [
        {
            'name': 'Super Administrator',
            'description': 'Full system access',
            'role_type': 'system',
            'permissions': [
                'view_user', 'add_user', 'change_user', 'delete_user',
                'change_user_role', 'change_user_status',
                'view_role', 'add_role', 'change_role', 'delete_role',
                'view_permission', 'add_permission', 'change_permission', 'delete_permission',
                'view_system_settings', 'change_system_settings',
                'view_audit_logs', 'export_data',
                'api_access', 'api_admin'
            ]
        },
        {
            'name': 'Administrator',
            'description': 'Administrative access',
            'role_type': 'organizational',
            'permissions': [
                'view_user', 'add_user', 'change_user',
                'change_user_role', 'change_user_status',
                'view_role', 'view_permission',
                'view_audit_logs',
                'api_access'
            ]
        },
        {
            'name': 'Manager',
            'description': 'Management access',
            'role_type': 'organizational',
            'permissions': [
                'view_user', 'change_user_status',
                'view_role', 'view_permission',
                'api_access'
            ]
        },
        {
            'name': 'Employee',
            'description': 'Standard employee access',
            'role_type': 'functional',
            'permissions': [
                'view_user',
                'api_access'
            ]
        },
        {
            'name': 'Client',
            'description': 'Client access',
            'role_type': 'functional',
            'permissions': [
                'api_access'
            ]
        },
        {
            'name': 'Guest',
            'description': 'Limited guest access',
            'role_type': 'functional',
            'permissions': []
        }
    ]
    
    created_roles = []
    
    for role_data in default_roles:
        permissions = role_data.pop('permissions', [])
        
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults=role_data
        )
        
        if created:
            created_roles.append(role)
            logger.info(f"Created role: {role.name}")
            
            # Assign permissions to role
            for perm_codename in permissions:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    RolePermission.objects.get_or_create(
                        role=role,
                        permission=permission,
                        defaults={'is_active': True}
                    )
                except Permission.DoesNotExist:
                    logger.warning(f"Permission not found: {perm_codename}")
    
    return created_roles


def assign_default_role_to_user(user, role_name='Client'):
    """
    Assign default role to a new user
    """
    try:
        from .models import UserRole
        
        role = Role.objects.get(name=role_name, is_active=True)
        
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={'is_active': True}
        )
        
        if created:
            logger.info(f"Assigned default role '{role_name}' to user: {user.email}")
        
        return user_role
        
    except Role.DoesNotExist:
        logger.error(f"Default role '{role_name}' not found")
        return None


def check_user_permission(user, permission_codename, resource=None):
    """
    Check if a user has a specific permission
    """
    if not user or not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Check direct user permissions
    from .models import UserPermission
    user_perm = UserPermission.objects.filter(
        user=user,
        permission__codename=permission_codename,
        is_active=True
    ).first()
    
    if user_perm:
        return user_perm.granted
    
    # Check role-based permissions
    user_permissions = user.get_permissions()
    return permission_codename in user_permissions


def get_user_resources(user, resource_type, permission_type='read'):
    """
    Get resources that a user has access to
    """
    if not user or not user.is_authenticated:
        return []
    
    if user.is_superuser:
        # Superuser has access to all resources
        return resource_type.objects.all()
    
    from django.contrib.contenttypes.models import ContentType
    from .models import ResourcePermission
    
    content_type = ContentType.objects.get_for_model(resource_type)
    
    # Get resource permissions for user
    resource_perms = ResourcePermission.objects.filter(
        user=user,
        content_type=content_type,
        permission_type=permission_type,
        is_active=True
    ).values_list('object_id', flat=True)
    
    # Get resources user has access to
    accessible_resources = resource_type.objects.filter(
        pk__in=resource_perms
    )
    
    # Also include resources owned by user
    if hasattr(resource_type, 'created_by'):
        owned_resources = resource_type.objects.filter(created_by=user)
        accessible_resources = accessible_resources.union(owned_resources)
    
    return accessible_resources


def create_audit_log(user, action_type, resource=None, permission=None, request=None, success=True, reason=None):
    """
    Create an audit log entry
    """
    try:
        from .models import AuditLog
        
        audit_data = {
            'user': user,
            'action_type': action_type,
            'success': success,
            'reason': reason or '',
        }
        
        if resource:
            audit_data['resource'] = str(resource)
        
        if permission:
            audit_data['permission'] = permission
        
        if request:
            audit_data.update({
                'ip_address': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:255],
                'request_path': request.path,
                'request_method': request.method,
            })
        
        AuditLog.objects.create(**audit_data)
        
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def cleanup_expired_permissions():
    """
    Clean up expired permissions and roles
    """
    from django.utils import timezone
    from .models import UserPermission, UserRole, ResourcePermission
    
    now = timezone.now()
    
    # Deactivate expired user permissions
    expired_user_perms = UserPermission.objects.filter(
        valid_until__lt=now,
        is_active=True
    )
    count = expired_user_perms.update(is_active=False)
    logger.info(f"Deactivated {count} expired user permissions")
    
    # Deactivate expired user roles
    expired_user_roles = UserRole.objects.filter(
        valid_until__lt=now,
        is_active=True
    )
    count = expired_user_roles.update(is_active=False)
    logger.info(f"Deactivated {count} expired user roles")
    
    # Deactivate expired resource permissions
    expired_resource_perms = ResourcePermission.objects.filter(
        valid_until__lt=now,
        is_active=True
    )
    count = expired_resource_perms.update(is_active=False)
    logger.info(f"Deactivated {count} expired resource permissions")


def get_user_effective_permissions(user):
    """
    Get all effective permissions for a user (including inherited from roles)
    """
    if not user or not user.is_authenticated:
        return set()
    
    if user.is_superuser:
        # Superuser has all permissions
        return set(Permission.objects.values_list('codename', flat=True))
    
    return user.get_permissions()
