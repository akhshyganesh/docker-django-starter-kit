"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
    DRF_DOCS_ENABLED = True
except ImportError:
    DRF_DOCS_ENABLED = False
from apps.core.views import health_check, security_headers_test

urlpatterns = [
    # Health check and security test endpoints
    path('health/', health_check, name='health_check'),
    path('security-test/', security_headers_test, name='security_test'),
    
    # Admin
    path('admin/', admin.site.urls),
]

if getattr(settings, 'ENABLE_DRF', True):
    if DRF_DOCS_ENABLED:
        urlpatterns += [
            path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
            path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
            path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
        ]
    urlpatterns += [
        path('api/v1/auth/', include('apps.authentication.urls')),
        path('api/v1/users/', include('apps.users.urls')),
        path('api/v1/permissions/', include('apps.permissions.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Add debug toolbar if available
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass
