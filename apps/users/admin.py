"""
Admin configuration for Users app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile, UserSession
from apps.permissions.models import UserRole, UserPermission

User = get_user_model()


class UserRoleInline(admin.TabularInline):
    """Inline for user roles"""
    model = UserRole
    fk_name = 'user'  # Specify which ForeignKey to use
    extra = 0
    fields = ['role', 'assigned_by', 'valid_from', 'valid_until', 'is_active']
    readonly_fields = ['assigned_by', 'created_at']


class UserPermissionInline(admin.TabularInline):
    """Inline for user permissions"""
    model = UserPermission
    fk_name = 'user'  # Specify which ForeignKey to use
    extra = 0
    fields = ['permission', 'granted', 'assigned_by', 'valid_from', 'valid_until', 'is_active']
    readonly_fields = ['assigned_by', 'created_at']


class UserProfileInline(admin.StackedInline):
    """Inline for user profile"""
    model = UserProfile
    fk_name = 'user'  # Specify which ForeignKey to use (though there's only one, being explicit)
    can_delete = False
    fields = [
        'company', 'job_title', 'department',
        'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country',
        'date_of_birth', 'gender',
        'website', 'linkedin', 'twitter',
        'email_notifications', 'sms_notifications', 'marketing_emails'
    ]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom user admin"""
    
    inlines = [UserProfileInline, UserRoleInline, UserPermissionInline]
    
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'user_type',
        'account_status', 'is_active', 'is_staff', 'mfa_enabled',
        'date_joined', 'last_login'
    ]
    
    list_filter = [
        'user_type', 'account_status', 'is_active', 'is_staff', 'is_superuser',
        'mfa_enabled', 'date_joined', 'last_login'
    ]
    
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'bio')
        }),
        ('Account Settings', {
            'fields': (
                'user_type', 'account_status', 'timezone', 'locale',
                'privacy_settings', 'notification_preferences'
            )
        }),
        ('Security', {
            'fields': (
                'firebase_uid', 'mfa_enabled', 'mfa_secret',
                'password_changed_at', 'login_attempts', 'locked_until'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('date_joined', 'last_login', 'last_activity')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'user_type'
            ),
        }),
    )
    
    readonly_fields = [
        'date_joined', 'last_login', 'last_activity', 'password_changed_at',
        'login_attempts', 'firebase_uid'
    ]
    
    actions = ['activate_users', 'deactivate_users', 'reset_login_attempts']
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        count = queryset.update(is_active=True, account_status='active')
        self.message_user(request, f'{count} users activated successfully.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        count = queryset.update(is_active=False, account_status='inactive')
        self.message_user(request, f'{count} users deactivated successfully.')
    deactivate_users.short_description = "Deactivate selected users"
    
    def reset_login_attempts(self, request, queryset):
        """Reset login attempts for selected users"""
        count = queryset.update(login_attempts=0, locked_until=None)
        self.message_user(request, f'Login attempts reset for {count} users.')
    reset_login_attempts.short_description = "Reset login attempts"


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin for user sessions"""
    
    list_display = [
        'user', 'session_key', 'ip_address', 'location',
        'created_at', 'last_activity', 'is_active'
    ]
    
    list_filter = ['is_active', 'created_at', 'last_activity']
    
    search_fields = ['user__email', 'ip_address', 'session_key']
    
    readonly_fields = [
        'session_key', 'user_agent', 'device_info',
        'created_at', 'last_activity'
    ]
    
    actions = ['terminate_sessions']
    
    def terminate_sessions(self, request, queryset):
        """Terminate selected sessions"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} sessions terminated successfully.')
    terminate_sessions.short_description = "Terminate selected sessions"
