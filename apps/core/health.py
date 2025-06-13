"""
Health check and monitoring endpoints for production deployment
"""
import redis
import logging
from django.conf import settings
from django.db import connections
from django.http import JsonResponse
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Comprehensive health check endpoint for production monitoring
    """
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    overall_healthy = True
    
    # Database Health Check
    try:
        db_conn = connections['default']
        db_conn.cursor()
        health_status['checks']['database'] = {
            'status': 'healthy',
            'message': 'Database connection successful'
        }
    except Exception as e:
        health_status['checks']['database'] = {
            'status': 'unhealthy',
            'message': f'Database connection failed: {str(e)}'
        }
        overall_healthy = False
    
    # Redis Cache Health Check
    try:
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['checks']['redis'] = {
                'status': 'healthy',
                'message': 'Redis cache working'
            }
        else:
            health_status['checks']['redis'] = {
                'status': 'unhealthy',
                'message': 'Redis cache not responding correctly'
            }
            overall_healthy = False
    except Exception as e:
        health_status['checks']['redis'] = {
            'status': 'unhealthy',
            'message': f'Redis connection failed: {str(e)}'
        }
        overall_healthy = False
    
    # Celery Health Check (if configured)
    try:
        from celery import current_app
        
        # Check if celery workers are active
        i = current_app.control.inspect()
        stats = i.stats()
        
        if stats:
            health_status['checks']['celery'] = {
                'status': 'healthy',
                'message': f'Celery workers active: {len(stats)}',
                'workers': list(stats.keys())
            }
        else:
            health_status['checks']['celery'] = {
                'status': 'unhealthy',
                'message': 'No active Celery workers found'
            }
            overall_healthy = False
    except Exception as e:
        health_status['checks']['celery'] = {
            'status': 'warning',
            'message': f'Celery check failed: {str(e)}'
        }
    
    # Set overall status
    if not overall_healthy:
        health_status['status'] = 'unhealthy'
    
    # Return appropriate HTTP status code
    http_status = status.HTTP_200_OK if overall_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_status, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def readiness_check(request):
    """
    Readiness check - determines if the application is ready to serve traffic
    """
    try:
        # Check if Django is properly configured
        from django.conf import settings
        
        # Check critical settings
        critical_settings = [
            'SECRET_KEY',
            'DATABASES',
            'ALLOWED_HOSTS'
        ]
        
        for setting_name in critical_settings:
            if not hasattr(settings, setting_name):
                return Response({
                    'status': 'not_ready',
                    'message': f'Missing critical setting: {setting_name}'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Check database connection
        from django.db import connection
        connection.cursor()
        
        return Response({
            'status': 'ready',
            'message': 'Application is ready to serve traffic'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'not_ready',
            'message': f'Application not ready: {str(e)}'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([AllowAny])
def liveness_check(request):
    """
    Liveness check - determines if the application is alive
    """
    return Response({
        'status': 'alive',
        'timestamp': timezone.now().isoformat(),
        'message': 'Application is alive'
    }, status=status.HTTP_200_OK)
