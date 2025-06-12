"""
Tests for user models and functionality
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from apps.permissions.models import Role, Permission, UserRole
from apps.permissions.utils import assign_default_role_to_user, create_default_permissions

User = get_user_model()


class UserModelTest(TestCase):
    """Test the custom User model"""
    
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpassword123'
        }
    
    def test_create_user(self):
        """Test creating a user with email"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
    
    def test_user_string_representation(self):
        """Test the string representation of user"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])
    
    def test_user_full_name(self):
        """Test the full_name property"""
        user = User.objects.create_user(**self.user_data)
        expected_name = f"{self.user_data['first_name']} {self.user_data['last_name']}"
        self.assertEqual(user.full_name, expected_name)
    
    def test_user_email_required(self):
        """Test that email is required"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpassword123'
            )
    
    def test_user_lock_unlock(self):
        """Test user lock and unlock functionality"""
        user = User.objects.create_user(**self.user_data)
        
        # Test locking
        user.lock_account(30)
        self.assertTrue(user.is_locked)
        self.assertEqual(user.account_status, 'locked')
        
        # Test unlocking
        user.unlock_account()
        self.assertFalse(user.is_locked)
        self.assertEqual(user.account_status, 'active')
        self.assertEqual(user.login_attempts, 0)
    
    def test_increment_login_attempts(self):
        """Test incrementing login attempts"""
        user = User.objects.create_user(**self.user_data)
        
        # Increment login attempts
        for i in range(1, 5):
            user.increment_login_attempts()
            self.assertEqual(user.login_attempts, i)
            self.assertFalse(user.is_locked)
        
        # 5th attempt should lock the account
        user.increment_login_attempts()
        self.assertEqual(user.login_attempts, 5)
        self.assertTrue(user.is_locked)


class UserPermissionTest(TestCase):
    """Test user permissions functionality"""
    
    def setUp(self):
        # Create default permissions and roles
        create_default_permissions()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_assign_default_role(self):
        """Test assigning default role to user"""
        role = assign_default_role_to_user(self.user, 'Client')
        
        self.assertIsNotNone(role)
        self.assertEqual(role.role.name, 'Client')
        self.assertEqual(role.user, self.user)
        self.assertTrue(role.is_active)
    
    def test_user_get_permissions(self):
        """Test getting user permissions"""
        # Assign a role to user
        assign_default_role_to_user(self.user, 'Client')
        
        permissions = self.user.get_permissions()
        self.assertIsInstance(permissions, set)
        # Client role should have api_access permission
        self.assertIn('api_access', permissions)
    
    def test_user_has_permission(self):
        """Test checking if user has specific permission"""
        # Assign Employee role
        assign_default_role_to_user(self.user, 'Employee')
        
        self.assertTrue(self.user.has_permission('api_access'))
        self.assertTrue(self.user.has_permission('view_user'))
        self.assertFalse(self.user.has_permission('add_user'))


class UserProfileTest(TestCase):
    """Test user profile functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
    
    def test_profile_created_automatically(self):
        """Test that profile is created automatically when user is created"""
        # Profile should be created by signal
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsNotNone(self.user.profile)
    
    def test_profile_string_representation(self):
        """Test profile string representation"""
        profile_str = str(self.user.profile)
        self.assertEqual(profile_str, f"{self.user.email} Profile")
