"""
Firebase authentication backend for Django REST Framework
"""
import logging
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from rest_framework import authentication, exceptions
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)
User = get_user_model()

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    try:
        if settings.FIREBASE_CONFIG and settings.FIREBASE_CONFIG.get('project_id'):
            cred = credentials.Certificate(settings.FIREBASE_CONFIG)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin SDK initialized successfully")
        else:
            logger.warning("Firebase configuration not found. Firebase authentication will be disabled.")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase Admin SDK: {e}")


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Firebase token authentication backend
    """
    
    def authenticate(self, request):
        """
        Authenticate the request using Firebase ID token
        """
        # Get the authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        # Extract the token
        token = auth_header.split(' ')[1]
        
        try:
            # Verify the Firebase token
            decoded_token = auth.verify_id_token(token)
            firebase_uid = decoded_token['uid']
            
            # Get or create user
            user = self.get_or_create_user(decoded_token)
            
            return (user, None)
            
        except FirebaseError as e:
            logger.warning(f"Firebase authentication failed: {e}")
            raise exceptions.AuthenticationFailed('Invalid Firebase token')
        except Exception as e:
            logger.error(f"Unexpected error during Firebase authentication: {e}")
            raise exceptions.AuthenticationFailed('Authentication failed')
    
    def get_or_create_user(self, decoded_token):
        """
        Get or create user from Firebase token data
        """
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        name = decoded_token.get('name', '')
        email_verified = decoded_token.get('email_verified', False)
        
        if not email:
            raise exceptions.AuthenticationFailed('Email not found in Firebase token')
        
        try:
            # Try to get existing user by Firebase UID
            user = User.objects.get(firebase_uid=firebase_uid)
            
            # Update user information if needed
            if user.email != email:
                user.email = email
                user.save()
            
            return user
            
        except User.DoesNotExist:
            # Try to get user by email
            try:
                user = User.objects.get(email=email)
                # Link Firebase UID to existing user
                user.firebase_uid = firebase_uid
                user.save()
                return user
            except User.DoesNotExist:
                # Create new user
                names = name.split(' ', 1) if name else ['', '']
                first_name = names[0] if names else ''
                last_name = names[1] if len(names) > 1 else ''
                
                user = User.objects.create_user(
                    email=email,
                    firebase_uid=firebase_uid,
                    first_name=first_name,
                    last_name=last_name,
                    account_status='active' if email_verified else 'pending',
                    user_type='client'
                )
                
                logger.info(f"New user created from Firebase: {email}")
                return user
    
    def authenticate_header(self, request):
        """
        Return the authentication header
        """
        return 'Bearer'


class MultiAuthenticationBackend:
    """
    Custom authentication backend that supports multiple authentication methods
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using email and password
        """
        if username is None or password is None:
            return None
        
        try:
            # Try to authenticate by email
            user = User.objects.get(email=username)
            
            # Check if account is locked
            if user.is_locked:
                logger.warning(f"Login attempt on locked account: {username}")
                return None
            
            # Check account status
            if user.account_status not in ['active']:
                logger.warning(f"Login attempt on inactive account: {username}")
                return None
            
            # Verify password
            if user.check_password(password):
                # Reset failed login attempts
                user.reset_login_attempts()
                user.last_login = timezone.now()
                user.save()
                
                logger.info(f"Successful login: {username}")
                return user
            else:
                # Increment failed login attempts
                user.increment_login_attempts()
                logger.warning(f"Failed login attempt: {username}")
                return None
                
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {username}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
