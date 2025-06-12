"""
Permission management API views
"""
import logging
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .models import Permission, Role, RolePermission, UserRole, AuditLog
from .permissions import DynamicPermission
from .serializers import (
    PermissionSerializer, RoleSerializer, RolePermissionSerializer,
    UserRoleSerializer, AuditLogSerializer
)

logger = logging.getLogger(__name__)
User = get_user_model()


class PermissionViewSet(viewsets.ModelViewSet):
    """
    Permission management viewset
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    
    required_permissions = {
        'list': 'view_permission',
        'retrieve': 'view_permission',
        'create': 'add_permission',
        'update': 'change_permission',
        'partial_update': 'change_permission',
        'destroy': 'delete_permission',
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['permission_type', 'is_active']
    search_fields = ['name', 'codename', 'description']
    ordering_fields = ['name', 'codename', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter active permissions"""
        return Permission.objects.filter(is_active=True)


class RoleViewSet(viewsets.ModelViewSet):
    """
    Role management viewset
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    
    required_permissions = {
        'list': 'view_role',
        'retrieve': 'view_role',
        'create': 'add_role',
        'update': 'change_role',
        'partial_update': 'change_role',
        'destroy': 'delete_role',
        'assign_permission': 'change_role',
        'revoke_permission': 'change_role',
        'assign_users': 'change_user_role',
        'revoke_users': 'change_user_role',
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter active roles"""
        return Role.objects.filter(is_active=True).prefetch_related('role_permissions__permission')
    
    @action(detail=True, methods=['post'])
    def assign_permission(self, request, pk=None):
        """Assign permission to role"""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response({
                'error': 'permission_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            permission = Permission.objects.get(id=permission_id, is_active=True)
        except Permission.DoesNotExist:
            return Response({
                'error': 'Permission not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if assignment already exists
        role_perm, created = RolePermission.objects.get_or_create(
            role=role,
            permission=permission,
            defaults={'is_active': True}
        )
        
        if not created and role_perm.is_active:
            return Response({
                'error': 'Role already has this permission'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not created:
            role_perm.is_active = True
            role_perm.save()
        
        logger.info(f"Permission '{permission.name}' assigned to role: {role.name}")
        
        return Response({
            'message': f"Permission '{permission.name}' assigned successfully"
        })
    
    @action(detail=True, methods=['post'])
    def revoke_permission(self, request, pk=None):
        """Revoke permission from role"""
        role = self.get_object()
        permission_id = request.data.get('permission_id')
        
        if not permission_id:
            return Response({
                'error': 'permission_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role_perm = RolePermission.objects.get(
                role=role,
                permission_id=permission_id,
                is_active=True
            )
            role_perm.is_active = False
            role_perm.save()
            
            logger.info(f"Permission '{role_perm.permission.name}' revoked from role: {role.name}")
            
            return Response({
                'message': f"Permission '{role_perm.permission.name}' revoked successfully"
            })
            
        except RolePermission.DoesNotExist:
            return Response({
                'error': 'Role does not have this permission'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get role permissions"""
        role = self.get_object()
        permissions = role.get_all_permissions()
        
        return Response({
            'permissions': [
                {
                    'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'permission_type': perm.permission_type
                }
                for perm in permissions
            ]
        })
    
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users with this role"""
        role = self.get_object()
        user_roles = UserRole.objects.filter(
            role=role,
            is_active=True
        ).select_related('user')
        
        users_data = []
        for user_role in user_roles:
            users_data.append({
                'id': user_role.user.id,
                'email': user_role.user.email,
                'full_name': user_role.user.full_name,
                'assigned_at': user_role.created_at,
                'assigned_by': user_role.assigned_by.email if user_role.assigned_by else None
            })
        
        return Response({
            'users': users_data
        })


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Audit log viewset (read-only)
    """
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    
    required_permissions = {
        'list': 'view_audit_logs',
        'retrieve': 'view_audit_logs',
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action_type', 'success', 'user']
    search_fields = ['resource', 'permission', 'reason']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        """Filter audit logs based on user permissions"""
        queryset = AuditLog.objects.all()
        
        # If not admin, users can only see their own audit logs
        if not (self.request.user.is_staff or self.request.user.user_type == 'admin'):
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get audit log statistics"""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)
        
        stats = {
            'total_logs': AuditLog.objects.count(),
            'last_24h': AuditLog.objects.filter(timestamp__gte=last_24h).count(),
            'last_7d': AuditLog.objects.filter(timestamp__gte=last_7d).count(),
            'last_30d': AuditLog.objects.filter(timestamp__gte=last_30d).count(),
            'success_rate': self._calculate_success_rate(),
            'top_actions': dict(
                AuditLog.objects.values('action_type').annotate(
                    count=Count('id')
                ).order_by('-count')[:10].values_list('action_type', 'count')
            ),
            'failed_actions': AuditLog.objects.filter(
                success=False,
                timestamp__gte=last_24h
            ).count()
        }
        
        return Response(stats)
    
    def _calculate_success_rate(self):
        """Calculate success rate percentage"""
        total = AuditLog.objects.count()
        if total == 0:
            return 100
        
        successful = AuditLog.objects.filter(success=True).count()
        return round((successful / total) * 100, 2)
