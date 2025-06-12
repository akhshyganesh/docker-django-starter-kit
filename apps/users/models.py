"""
Custom User model with enhanced security features
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from apps.core.models import AuditModel


class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin, AuditModel):
    """
    Custom User model with enhanced security features
    """
    
    # User Types
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
        ('client', 'Client'),
        ('guest', 'Guest'),
    ]
    
    # Account Status
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('locked', 'Locked'),
        ('pending', 'Pending Verification'),
    ]
    
    # Basic Information
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9._-]+$',
                message='Username can only contain letters, numbers, dots, hyphens, and underscores.'
            )
        ]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Profile Information
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.'
            )
        ]
    )
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    user_timezone = models.CharField(max_length=50, default='UTC')
    locale = models.CharField(max_length=10, default='en')
    
    # Account Status
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='client')
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='pending')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Security Fields
    firebase_uid = models.CharField(max_length=128, unique=True, null=True, blank=True, db_index=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=32, blank=True)
    backup_codes = models.JSONField(default=list, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    
    # Login Tracking
    login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Privacy Settings
    privacy_settings = models.JSONField(default=dict, blank=True)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['firebase_uid']),
            models.Index(fields=['user_type', 'account_status']),
        ]
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return the full name of the user"""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_locked(self):
        """Check if the account is locked"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock the account for a specified duration"""
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.account_status = 'locked'
        self.save()
    
    def unlock_account(self):
        """Unlock the account"""
        self.locked_until = None
        self.login_attempts = 0
        self.account_status = 'active'
        self.save()
    
    def increment_login_attempts(self):
        """Increment failed login attempts"""
        self.login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Lock account after 5 failed attempts
        if self.login_attempts >= 5:
            self.lock_account()
        
        self.save()
    
    def reset_login_attempts(self):
        """Reset login attempts after successful login"""
        self.login_attempts = 0
        self.last_failed_login = None
        self.save()
    
    def update_last_activity(self):
        """Update last activity timestamp"""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
    
    def get_permissions(self):
        """Get all permissions for the user"""
        from apps.permissions.models import UserPermission, RolePermission
        
        permissions = set()
        
        # Direct user permissions
        user_perms = UserPermission.objects.filter(
            user=self,
            is_active=True
        ).select_related('permission')
        
        for user_perm in user_perms:
            permissions.add(user_perm.permission.codename)
        
        # Role-based permissions
        role_perms = RolePermission.objects.filter(
            role__users=self,
            role__is_active=True,
            is_active=True
        ).select_related('permission')
        
        for role_perm in role_perms:
            permissions.add(role_perm.permission.codename)
        
        return permissions
    
    def has_permission(self, permission_codename):
        """Check if user has a specific permission"""
        return permission_codename in self.get_permissions()


class UserSession(models.Model):
    """Track user sessions for security monitoring"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    device_info = models.JSONField(default=dict, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def terminate(self):
        """Terminate the session"""
        self.is_active = False
        self.save()


class UserProfile(AuditModel):
    """Extended user profile information"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Professional Information
    company = models.CharField(max_length=100, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    
    # Address Information
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Additional Information
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20,
        choices=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
            ('prefer_not_to_say', 'Prefer not to say'),
        ],
        blank=True
    )
    
    # Social Links
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.email} Profile"
