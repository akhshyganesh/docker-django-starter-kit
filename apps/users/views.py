"""
User management API views
"""
import logging
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.serializers import UserSerializer, UserProfileSerializer
from apps.permissions.permissions import DynamicPermission, IsAdminOrReadOnly
from apps.permissions.models import Role, UserRole

logger = logging.getLogger(__name__)
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    User management viewset with RBAC/ABAC permissions
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    
    # Required permissions for different actions
    required_permissions = {
        'list': 'view_user',
        'retrieve': 'view_user',
        'create': 'add_user',
        'update': 'change_user',
        'partial_update': 'change_user',
        'destroy': 'delete_user',
        'assign_role': 'change_user_role',
        'revoke_role': 'change_user_role',
        'activate': 'change_user_status',
        'deactivate': 'change_user_status',
        'lock': 'change_user_status',
        'unlock': 'change_user_status',
    }
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user_type', 'account_status', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering_fields = ['email', 'first_name', 'last_name', 'date_joined', 'last_login']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        queryset = User.objects.select_related('profile').prefetch_related('user_roles__role')
        
        # If not admin, users can only see active users
        if not (self.request.user.is_staff or self.request.user.user_type == 'admin'):
            queryset = queryset.filter(is_active=True, account_status='active')
        
        return queryset
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action in ['retrieve', 'profile']:
            return UserProfileSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """Update current user profile"""
        serializer = self.get_serializer(
            request.user, 
            data=request.data, 
            partial=request.method == 'PATCH'
        )
        
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User profile updated: {request.user.email}")
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Assign role to user"""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response({
                'error': 'role_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            role = Role.objects.get(id=role_id, is_active=True)
        except Role.DoesNotExist:
            return Response({
                'error': 'Role not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if role assignment already exists
        user_role, created = UserRole.objects.get_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by': request.user,
                'is_active': True
            }
        )
        
        if not created and user_role.is_active:
            return Response({
                'error': 'User already has this role'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not created:
            user_role.is_active = True
            user_role.assigned_by = request.user
            user_role.save()
        
        logger.info(f"Role '{role.name}' assigned to user: {user.email} by {request.user.email}")
        
        return Response({
            'message': f"Role '{role.name}' assigned successfully"
        })
    
    @action(detail=True, methods=['post'])
    def revoke_role(self, request, pk=None):
        """Revoke role from user"""
        user = self.get_object()
        role_id = request.data.get('role_id')
        
        if not role_id:
            return Response({
                'error': 'role_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_role = UserRole.objects.get(
                user=user,
                role_id=role_id,
                is_active=True
            )
            user_role.is_active = False
            user_role.save()
            
            logger.info(f"Role '{user_role.role.name}' revoked from user: {user.email} by {request.user.email}")
            
            return Response({
                'message': f"Role '{user_role.role.name}' revoked successfully"
            })
            
        except UserRole.DoesNotExist:
            return Response({
                'error': 'User does not have this role'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate user account"""
        user = self.get_object()
        
        if user.account_status == 'active':
            return Response({
                'error': 'User is already active'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.account_status = 'active'
        user.is_active = True
        user.save()
        
        logger.info(f"User activated: {user.email} by {request.user.email}")
        
        return Response({
            'message': 'User activated successfully'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate user account"""
        user = self.get_object()
        
        if user == request.user:
            return Response({
                'error': 'Cannot deactivate your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.account_status = 'inactive'
        user.is_active = False
        user.save()
        
        logger.info(f"User deactivated: {user.email} by {request.user.email}")
        
        return Response({
            'message': 'User deactivated successfully'
        })
    
    @action(detail=True, methods=['post'])
    def lock(self, request, pk=None):
        """Lock user account"""
        user = self.get_object()
        duration = request.data.get('duration', 30)  # minutes
        
        if user == request.user:
            return Response({
                'error': 'Cannot lock your own account'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.lock_account(duration)
        
        logger.info(f"User locked: {user.email} by {request.user.email}")
        
        return Response({
            'message': f'User locked for {duration} minutes'
        })
    
    @action(detail=True, methods=['post'])
    def unlock(self, request, pk=None):
        """Unlock user account"""
        user = self.get_object()
        
        user.unlock_account()
        
        logger.info(f"User unlocked: {user.email} by {request.user.email}")
        
        return Response({
            'message': 'User unlocked successfully'
        })
    
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get user permissions"""
        user = self.get_object()
        permissions = user.get_permissions()
        
        return Response({
            'permissions': list(permissions)
        })
    
    @action(detail=True, methods=['get'])
    def activity(self, request, pk=None):
        """Get user activity log"""
        user = self.get_object()
        
        # Get recent audit logs for this user
        from apps.permissions.models import AuditLog
        logs = AuditLog.objects.filter(
            user=user
        ).order_by('-timestamp')[:20]
        
        activity_data = []
        for log in logs:
            activity_data.append({
                'action': log.action_type,
                'timestamp': log.timestamp,
                'ip_address': log.ip_address,
                'success': log.success,
                'details': log.details
            })
        
        return Response({
            'activity': activity_data
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        from django.db.models import Count
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'inactive_users': User.objects.filter(is_active=False).count(),
            'locked_users': User.objects.filter(account_status='locked').count(),
            'users_by_type': dict(
                User.objects.values('user_type').annotate(
                    count=Count('id')
                ).values_list('user_type', 'count')
            ),
            'users_by_status': dict(
                User.objects.values('account_status').annotate(
                    count=Count('id')
                ).values_list('account_status', 'count')
            )
        }
        
        return Response(stats)
