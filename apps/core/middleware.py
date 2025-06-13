"""
Custom security middleware for enhanced protection
"""

import time
import logging
from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses
    """
    
    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response['Permissions-Policy'] = (
            'accelerometer=(), camera=(), geolocation=(), '
            'gyroscope=(), magnetometer=(), microphone=(), '
            'payment=(), usb=()'
        )
        
        # Content Security Policy (basic)
        if not hasattr(settings, 'CSP_DEFAULT_SRC'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none';"
            )
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware
    """
    
    def process_request(self, request):
        if not getattr(settings, 'RATELIMIT_ENABLE', True):
            return None
            
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Different rate limits for different endpoints
        if request.path.startswith('/api/v1/auth/'):
            # Stricter limit for auth endpoints
            cache_key = f'rate_limit_auth_{ip}'
            limit = 10  # 10 requests per minute
            window = 60
        elif request.path.startswith('/api/'):
            # General API rate limit
            cache_key = f'rate_limit_api_{ip}'
            limit = 100  # 100 requests per minute
            window = 60
        else:
            # General rate limit
            cache_key = f'rate_limit_general_{ip}'
            limit = 200  # 200 requests per minute
            window = 60
        
        # Check current count
        current_count = cache.get(cache_key, 0)
        
        if current_count >= limit:
            logger.warning(f"Rate limit exceeded for IP {ip} on {request.path}")
            return HttpResponse(
                '{"error": "Rate limit exceeded. Please try again later."}',
                status=429,
                content_type='application/json'
            )
        
        # Increment counter
        cache.set(cache_key, current_count + 1, window)
        
        return None


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security-relevant events
    """
    
    def process_request(self, request):
        # Log suspicious requests
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Check for common attack patterns
        suspicious_patterns = [
            'sqlmap', 'nikto', 'nmap', 'dirb', 'dirbuster',
            'burp', 'havij', 'union select', 'script>',
            'javascript:', 'vbscript:', 'onload=', 'onerror='
        ]
        
        request_data = str(request.GET) + str(request.POST) + user_agent.lower()
        
        for pattern in suspicious_patterns:
            if pattern in request_data.lower():
                logger.warning(
                    f"Suspicious request detected from {request.META.get('REMOTE_ADDR')}: "
                    f"{pattern} in {request.path}"
                )
                break
        
        return None
    
    def process_response(self, request, response):
        # Log failed authentication attempts
        if (response.status_code == 401 and 
            request.path.startswith('/api/v1/auth/')):
            logger.warning(
                f"Failed authentication attempt from {request.META.get('REMOTE_ADDR')} "
                f"to {request.path}"
            )
        
        return response


class IPWhitelistMiddleware(MiddlewareMixin):
    """
    IP whitelist middleware for admin access
    """
    
    def process_request(self, request):
        # Only apply to admin URLs
        if not request.path.startswith('/admin/'):
            return None
        
        # Get allowed IPs from settings
        allowed_ips = getattr(settings, 'ADMIN_ALLOWED_IPS', ['127.0.0.1', '::1'])
        
        if not allowed_ips:
            return None
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        if ip not in allowed_ips:
            logger.warning(f"Unauthorized admin access attempt from IP {ip}")
            return HttpResponse(
                '{"error": "Access denied"}',
                status=403,
                content_type='application/json'
            )
        
        return None
