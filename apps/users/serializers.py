"""
User serializers for API endpoints
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from apps.permissions.models import Role, UserRole

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'phone_number', 'password', 'password_confirm'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('Account is disabled')
            
            if user.is_locked:
                raise serializers.ValidationError('Account is locked')
            
            attrs['user'] = user
            return attrs
        
        raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details
    """
    full_name = serializers.ReadOnlyField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone_number', 'avatar', 'bio', 'timezone', 'locale',
            'user_type', 'account_status', 'is_staff', 'is_active',
            'mfa_enabled', 'date_joined', 'last_login', 'last_activity',
            'roles', 'permissions'
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'last_activity',
            'account_status', 'user_type'
        ]
    
    def get_roles(self, obj):
        """Get user roles"""
        user_roles = UserRole.objects.filter(
            user=obj,
            is_active=True
        ).select_related('role')
        
        return [
            {
                'id': ur.role.id,
                'name': ur.role.name,
                'role_type': ur.role.role_type
            }
            for ur in user_roles
        ]
    
    def get_permissions(self, obj):
        """Get user permissions"""
        return list(obj.get_permissions())


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed user profile
    """
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'phone_number', 'avatar', 'bio', 'timezone', 'locale',
            'user_type', 'account_status', 'mfa_enabled',
            'privacy_settings', 'notification_preferences',
            'date_joined', 'last_login', 'profile'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']
    
    def get_profile(self, obj):
        """Get extended profile information"""
        if hasattr(obj, 'profile'):
            return {
                'company': obj.profile.company,
                'job_title': obj.profile.job_title,
                'department': obj.profile.department,
                'city': obj.profile.city,
                'country': obj.profile.country,
                'website': obj.profile.website,
                'linkedin': obj.profile.linkedin,
                'twitter': obj.profile.twitter,
            }
        return {}


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset request
    """
    email = serializers.EmailField()
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError('User with this email does not exist')
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation
    """
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs


class FirebaseAuthSerializer(serializers.Serializer):
    """
    Serializer for Firebase authentication
    """
    firebase_token = serializers.CharField()
    
    def validate_firebase_token(self, value):
        # Token validation is handled in the authentication backend
        return value


class MFASetupSerializer(serializers.Serializer):
    """
    Serializer for MFA setup
    """
    secret = serializers.CharField(read_only=True)
    qr_code = serializers.CharField(read_only=True)
    backup_codes = serializers.ListField(child=serializers.CharField(), read_only=True)


class MFAVerifySerializer(serializers.Serializer):
    """
    Serializer for MFA verification
    """
    token = serializers.CharField(max_length=6, min_length=6)
    
    def validate_token(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('Token must be numeric')
        return value
