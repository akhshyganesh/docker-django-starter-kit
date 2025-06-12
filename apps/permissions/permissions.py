"""
Dynamic permission system for RBAC and ABAC
"""
import logging
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions
from rest_framework.request import Request
from .models import Permission, Role, UserRole, UserPermission, ResourcePermission, PolicyRule, AuditLog

logger = logging.getLogger(__name__)
User = get_user_model()


class DynamicPermission(permissions.BasePermission):
    """
    Dynamic permission class that implements both RBAC and ABAC
    """
    
    def has_permission(self, request, view):
        """
        Global permission check
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser bypass
        if request.user.is_superuser:
            return True
        
        # Check if user account is active and not locked
        if not request.user.is_active or request.user.is_locked:
            self._log_access_denied(request, "Account inactive or locked")
            return False
        
        # Get required permission from view
        required_permission = self._get_required_permission(request, view)
        if not required_permission:
            return True  # No specific permission required
        
        # Check permission using RBAC/ABAC
        has_perm = self._check_permission(request.user, required_permission, request, view)
        
        if has_perm:
            self._log_access_granted(request, required_permission)
        else:
            self._log_access_denied(request, f"Missing permission: {required_permission}")
        
        return has_perm
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission check
        """
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Superuser bypass
        if request.user.is_superuser:
            return True
        
        # Check resource-based permissions
        return self._check_resource_permission(request.user, obj, request.method.lower(), request)
    
    def _get_required_permission(self, request, view):
        """
        Get required permission from view configuration
        """
        # Check view-level permission requirement
        if hasattr(view, 'required_permissions'):
            perms = view.required_permissions
            if isinstance(perms, dict):
                method = request.method.lower()
                return perms.get(method, perms.get('default'))
            elif isinstance(perms, str):
                return perms
            elif isinstance(perms, list):
                return perms[0] if perms else None
        
        # Default permission based on action
        if hasattr(view, 'action'):
            action = view.action
            model_name = getattr(view, 'model', None)
            if model_name:
                model_name = model_name._meta.model_name
                return f"{action}_{model_name}"
        
        # Default permission based on HTTP method
        method_perms = {
            'get': 'view',
            'post': 'add',
            'put': 'change',
            'patch': 'change',
            'delete': 'delete',
        }
        
        method = request.method.lower()
        action = method_perms.get(method, 'view')
        
        if hasattr(view, 'model') and view.model:
            model_name = view.model._meta.model_name
            return f"{action}_{model_name}"
        
        return None
    
    def _check_permission(self, user, permission_codename, request, view):
        """
        Check if user has the required permission using RBAC and ABAC
        """
        try:
            # 1. Check direct user permissions (highest priority)
            user_perm = UserPermission.objects.filter(
                user=user,
                permission__codename=permission_codename,
                is_active=True
            ).first()
            
            if user_perm:
                if not user_perm.granted:
                    return False  # Explicit deny
                
                # Check time-based constraints
                if not self._check_time_constraints(user_perm):
                    return False
                
                # Check ABAC conditions
                if self._evaluate_abac_conditions(user, user_perm.conditions, request, view):
                    return True
            
            # 2. Check role-based permissions
            user_roles = UserRole.objects.filter(
                user=user,
                is_active=True
            ).select_related('role')
            
            for user_role in user_roles:
                if not self._check_time_constraints(user_role):
                    continue
                
                # Check if role has the permission
                role_perm = user_role.role.role_permissions.filter(
                    permission__codename=permission_codename,
                    is_active=True
                ).first()
                
                if role_perm:
                    if not self._check_time_constraints(role_perm):
                        continue
                    
                    # Check ABAC conditions
                    if self._evaluate_abac_conditions(user, role_perm.conditions, request, view):
                        return True
            
            # 3. Check policy rules (ABAC)
            if self._check_policy_rules(user, permission_codename, request, view):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Permission check error: {e}")
            return False
    
    def _check_resource_permission(self, user, obj, action, request):
        """
        Check resource-level permissions
        """
        try:
            content_type = ContentType.objects.get_for_model(obj)
            
            # Check resource permissions
            resource_perm = ResourcePermission.objects.filter(
                user=user,
                content_type=content_type,
                object_id=obj.pk,
                permission_type=action,
                is_active=True
            ).first()
            
            if resource_perm:
                if not self._check_time_constraints(resource_perm):
                    return False
                
                return self._evaluate_abac_conditions(user, resource_perm.conditions, request, obj)
            
            # Check if user owns the object
            if hasattr(obj, 'created_by') and obj.created_by == user:
                return True
            
            if hasattr(obj, 'owner') and obj.owner == user:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Resource permission check error: {e}")
            return False
    
    def _check_time_constraints(self, permission_obj):
        """
        Check time-based constraints
        """
        from django.utils import timezone
        now = timezone.now()
        
        if hasattr(permission_obj, 'valid_from') and permission_obj.valid_from:
            if now < permission_obj.valid_from:
                return False
        
        if hasattr(permission_obj, 'valid_until') and permission_obj.valid_until:
            if now > permission_obj.valid_until:
                return False
        
        return True
    
    def _evaluate_abac_conditions(self, user, conditions, request, context=None):
        """
        Evaluate ABAC conditions
        """
        if not conditions:
            return True
        
        try:
            # User attributes
            user_attrs = {
                'user_type': user.user_type,
                'account_status': user.account_status,
                'email_domain': user.email.split('@')[1] if '@' in user.email else '',
                'is_staff': user.is_staff,
                'mfa_enabled': user.mfa_enabled,
            }
            
            # Request attributes
            request_attrs = {
                'method': request.method,
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_secure': request.is_secure(),
            }
            
            # Time attributes
            from django.utils import timezone
            now = timezone.now()
            time_attrs = {
                'hour': now.hour,
                'day_of_week': now.weekday(),
                'is_weekend': now.weekday() >= 5,
            }
            
            # Combine all attributes
            all_attrs = {
                'user': user_attrs,
                'request': request_attrs,
                'time': time_attrs,
                'context': context,
            }
            
            # Simple condition evaluation
            return self._evaluate_conditions(conditions, all_attrs)
            
        except Exception as e:
            logger.error(f"ABAC condition evaluation error: {e}")
            return False
    
    def _evaluate_conditions(self, conditions, attributes):
        """
        Simple condition evaluation engine
        """
        if not conditions:
            return True
        
        # This is a simplified implementation
        # In production, you'd want a more sophisticated rule engine
        
        for condition_key, condition_value in conditions.items():
            if '.' in condition_key:
                # Nested attribute access (e.g., user.user_type)
                keys = condition_key.split('.')
                current = attributes
                
                for key in keys:
                    if isinstance(current, dict) and key in current:
                        current = current[key]
                    else:
                        return False
                
                if current != condition_value:
                    return False
            else:
                # Direct attribute access
                if condition_key not in attributes or attributes[condition_key] != condition_value:
                    return False
        
        return True
    
    def _check_policy_rules(self, user, permission_codename, request, view):
        """
        Check ABAC policy rules
        """
        try:
            # Get applicable policy rules
            rules = PolicyRule.objects.filter(
                is_active=True
            ).order_by('-priority')
            
            for rule in rules:
                if rule.evaluate(user, permission_codename, request.method.lower()):
                    return rule.rule_type == 'allow'
            
            return False
            
        except Exception as e:
            logger.error(f"Policy rule evaluation error: {e}")
            return False
    
    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _log_access_granted(self, request, permission):
        """Log successful access"""
        try:
            AuditLog.objects.create(
                user=request.user,
                action_type='access_granted',
                permission=permission,
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                request_path=request.path,
                request_method=request.method,
                success=True,
            )
        except Exception as e:
            logger.error(f"Failed to log access granted: {e}")
    
    def _log_access_denied(self, request, reason):
        """Log denied access"""
        try:
            AuditLog.objects.create(
                user=request.user if hasattr(request, 'user') and request.user.is_authenticated else None,
                action_type='access_denied',
                ip_address=self._get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
                request_path=request.path,
                request_method=request.method,
                reason=reason,
                success=False,
            )
        except Exception as e:
            logger.error(f"Failed to log access denied: {e}")


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the owner
        return obj.created_by == request.user


class IsSameUserOrReadOnly(permissions.BasePermission):
    """
    Permission for user profiles - users can only edit their own profile
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to the same user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        return obj == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission that allows admins to edit, others can only read
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and (
            request.user.is_staff or 
            request.user.user_type == 'admin'
        )
