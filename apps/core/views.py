"""
Core views for the SAAS application
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

logger = logging.getLogger(__name__)


def csrf_failure(request, reason=""):
    """
    Handle CSRF failures with a JSON response
    """
    logger.warning(f"CSRF failure for {request.META.get('REMOTE_ADDR', 'Unknown IP')}: {reason}")
    
    return JsonResponse({
        'error': 'CSRF verification failed',
        'message': 'Request could not be verified due to security reasons.',
        'code': 'CSRF_FAILURE'
    }, status=403)


@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for monitoring
    """
    return JsonResponse({
        'status': 'healthy',
        'service': 'django-saas-app'
    })


@require_http_methods(["GET"])
def security_headers_test(request):
    """
    Test endpoint to verify security headers are working
    """
    response = JsonResponse({
        'message': 'Security headers active',
        'headers_applied': [
            'X-Frame-Options',
            'X-Content-Type-Options',
            'X-XSS-Protection',
            'Content-Security-Policy',
            'Strict-Transport-Security',
            'Referrer-Policy'
        ]
    })
    
    # Additional security headers
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response
