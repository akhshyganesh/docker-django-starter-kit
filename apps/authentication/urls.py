"""
Authentication URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthenticationViewSet, MFAViewSet, user_profile, health_check

router = DefaultRouter()
router.register(r'', AuthenticationViewSet, basename='auth')
router.register(r'mfa', MFAViewSet, basename='mfa')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', user_profile, name='user-profile'),
    path('health/', health_check, name='health-check'),
]
