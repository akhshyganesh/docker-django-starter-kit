"""
Authentication API views
"""
import logging
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
from django.contrib.auth import get_user_model, login, logout
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, generics, viewsets
from rest_framework.authtoken.models import Token
from knox.models import AuthToken
from apps.users.serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserSerializer,
    PasswordChangeSerializer, PasswordResetSerializer, 
    PasswordResetConfirmSerializer, FirebaseAuthSerializer,
    MFASetupSerializer, MFAVerifySerializer
)
from apps.permissions.permissions import DynamicPermission

logger = logging.getLogger(__name__)
User = get_user_model()


class AuthenticationViewSet(viewsets.GenericViewSet):
    """
    Authentication endpoints
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        """User registration"""
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Create Knox token
            instance, token = AuthToken.objects.create(user)
            
            # Log successful registration
            logger.info(f"New user registered: {user.email}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'Registration successful'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        """User login with email and password"""
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login and activity
            user.last_login = timezone.now()
            user.last_activity = timezone.now()
            user.save()
            
            # Create Knox token
            instance, token = AuthToken.objects.create(user)
            
            # Log successful login
            logger.info(f"User logged in: {user.email}")
            
            return Response({
                'user': UserSerializer(user).data,
                'token': token,
                'message': 'Login successful'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def firebase_login(self, request):
        """Firebase authentication"""
        serializer = FirebaseAuthSerializer(data=request.data)
        if serializer.is_valid():
            # Firebase authentication is handled by the FirebaseAuthentication backend
            # This endpoint is mainly for explicit Firebase token exchange
            
            # The user is already authenticated via Firebase at this point
            if request.user.is_authenticated:
                # Create Knox token for consistent token management
                instance, token = AuthToken.objects.create(request.user)
                
                # Update last activity
                request.user.update_last_activity()
                
                logger.info(f"User authenticated via Firebase: {request.user.email}")
                
                return Response({
                    'user': UserSerializer(request.user).data,
                    'token': token,
                    'message': 'Firebase authentication successful'
                })
            
            return Response({
                'error': 'Firebase authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """User logout"""
        try:
            # Delete the Knox token
            request._auth.delete()
            
            logger.info(f"User logged out: {request.user.email}")
            
            return Response({
                'message': 'Logout successful'
            })
        except Exception as e:
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout_all(self, request):
        """Logout from all devices"""
        try:
            # Delete all Knox tokens for the user
            AuthToken.objects.filter(user=request.user).delete()
            
            logger.info(f"User logged out from all devices: {request.user.email}")
            
            return Response({
                'message': 'Logged out from all devices'
            })
        except Exception as e:
            return Response({
                'error': 'Logout failed'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            
            # Update password changed timestamp
            request.user.password_changed_at = timezone.now()
            request.user.save()
            
            # Invalidate all existing tokens
            AuthToken.objects.filter(user=request.user).delete()
            
            # Create new token
            instance, token = AuthToken.objects.create(request.user)
            
            logger.info(f"Password changed for user: {request.user.email}")
            
            return Response({
                'token': token,
                'message': 'Password changed successfully'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        """Request password reset"""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # In a real application, you would send a password reset email here
            # For this demo, we'll just return a success message
            
            logger.info(f"Password reset requested for: {email}")
            
            return Response({
                'message': 'Password reset email sent (if user exists)'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password_confirm(self, request):
        """Confirm password reset"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            # In a real application, you would validate the reset token
            # and update the user's password
            
            return Response({
                'message': 'Password reset successful'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MFAViewSet(viewsets.GenericViewSet):
    """
    Multi-Factor Authentication endpoints
    """
    permission_classes = [IsAuthenticated, DynamicPermission]
    
    @action(detail=False, methods=['post'])
    def setup(self, request):
        """Setup MFA for user"""
        user = request.user
        
        if user.mfa_enabled:
            return Response({
                'error': 'MFA is already enabled'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4) for _ in range(10)]
        
        # Create TOTP URI
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name="SAAS Application"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        qr_data = base64.b64encode(buffer.getvalue()).decode()
        
        # Store in user (not saved yet - will be saved on verification)
        user.mfa_secret = secret
        user.backup_codes = backup_codes
        
        return Response({
            'secret': secret,
            'qr_code': f"data:image/png;base64,{qr_data}",
            'backup_codes': backup_codes,
            'message': 'Scan the QR code with your authenticator app and verify to enable MFA'
        })
    
    @action(detail=False, methods=['post'])
    def verify(self, request):
        """Verify MFA setup"""
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            if not user.mfa_secret:
                return Response({
                    'error': 'MFA setup not initiated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify TOTP token
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(token):
                user.mfa_enabled = True
                user.save()
                
                logger.info(f"MFA enabled for user: {user.email}")
                
                return Response({
                    'message': 'MFA enabled successfully'
                })
            else:
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def disable(self, request):
        """Disable MFA"""
        user = request.user
        serializer = MFAVerifySerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            if not user.mfa_enabled:
                return Response({
                    'error': 'MFA is not enabled'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify TOTP token
            totp = pyotp.TOTP(user.mfa_secret)
            if totp.verify(token):
                user.mfa_enabled = False
                user.mfa_secret = ''
                user.backup_codes = []
                user.save()
                
                logger.info(f"MFA disabled for user: {user.email}")
                
                return Response({
                    'message': 'MFA disabled successfully'
                })
            else:
                return Response({
                    'error': 'Invalid verification code'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get MFA status"""
        user = request.user
        return Response({
            'mfa_enabled': user.mfa_enabled,
            'backup_codes_count': len(user.backup_codes)
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'version': '1.0.0'
    })
