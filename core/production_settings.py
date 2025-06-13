"""
Production-specific Django settings
Override base settings for production deployment
"""
from .settings import *
import os
import logging.config

# =================================================================
# PRODUCTION SECURITY SETTINGS
# =================================================================

# DEBUG must be False in production
DEBUG = False

# Ensure SECRET_KEY is set from environment
if not SECRET_KEY or SECRET_KEY == 'django-insecure-change-me-in-production':
    raise ValueError(
        "SECRET_KEY must be set to a secure value in production. "
        "Generate one using: python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'"
    )

# Validate ALLOWED_HOSTS is configured
if not ALLOWED_HOSTS or ALLOWED_HOSTS == ['localhost', '127.0.0.1']:
    raise ValueError(
        "ALLOWED_HOSTS must be configured with your production domain(s). "
        "Set ALLOWED_HOSTS in your .env file."
    )

# =================================================================
# ENHANCED SECURITY HEADERS
# =================================================================

# Force HTTPS in production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Secure cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# HSTS Settings
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Additional security headers
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# =================================================================
# SESSION SECURITY
# =================================================================

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# =================================================================
# DATABASE OPTIMIZATION
# =================================================================

# Database connection optimization
DATABASES['default'].update({
    'CONN_MAX_AGE': 600,
    'OPTIONS': {
        'MAX_CONNS': 20,
        'sslmode': 'prefer',
    }
})

# =================================================================
# CACHE CONFIGURATION
# =================================================================

# Enhanced Redis cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'saas_prod',
        'TIMEOUT': 300,
    }
}

# =================================================================
# LOGGING CONFIGURATION
# =================================================================

# Production logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} {name} {process:d} {thread:d} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'simple': {
            'format': '[{asctime}] {levelname} {message}',
            'style': '{',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'security.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 10,
            'formatter': 'json',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['security_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# =================================================================
# EMAIL CONFIGURATION
# =================================================================

# Production email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 30
EMAIL_USE_LOCALTIME = True

# Email for error reporting
ADMINS = [
    ('Admin', config('ADMIN_EMAIL', default='admin@example.com')),
]
MANAGERS = ADMINS

# =================================================================
# STATIC AND MEDIA FILES
# =================================================================

# Static files configuration for production
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# AWS S3 Configuration (optional)
USE_S3 = config('USE_S3', default=False, cast=bool)

if USE_S3:
    AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Use S3 for static and media files
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# =================================================================
# CELERY PRODUCTION CONFIGURATION
# =================================================================

# Enhanced Celery configuration for production
CELERY_BROKER_URL = config('REDIS_URL', default='redis://redis:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://redis:6379/0')

# Celery optimization
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes
CELERY_TASK_TIME_LIMIT = 600  # 10 minutes

# Task routing
CELERY_TASK_ROUTES = {
    'apps.users.tasks.*': {'queue': 'users'},
    'apps.authentication.tasks.*': {'queue': 'auth'},
}

# =================================================================
# MONITORING AND HEALTH CHECKS
# =================================================================

# Health check configuration
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # Maximum disk usage percentage
    'MEMORY_MIN': 100,     # Minimum available memory in MB
}

# =================================================================
# RATE LIMITING
# =================================================================

# Enhanced rate limiting for production
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'

# =================================================================
# CORS CONFIGURATION
# =================================================================

# Strict CORS settings for production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='', cast=lambda v: [s.strip() for s in v.split(',') if s.strip()])

if not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

CORS_ALLOW_CREDENTIALS = True
CORS_PREFLIGHT_MAX_AGE = 86400

# =================================================================
# API THROTTLING
# =================================================================

# Enhanced REST framework configuration for production
REST_FRAMEWORK.update({
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'auth': '5/min',
        'password_reset': '3/hour',
    },
})

# =================================================================
# DJANGO AXES CONFIGURATION
# =================================================================

# Enhanced brute force protection
AXES_FAILURE_LIMIT = 3
AXES_COOLOFF_TIME = 24  # 24 hours
AXES_LOCK_OUT_AT_FAILURE = True
AXES_USE_USER_AGENT = True
AXES_LOCKOUT_CALLABLE = 'axes.lockout.lockout'
AXES_RESET_ON_SUCCESS = True

# =================================================================
# CONTENT SECURITY POLICY
# =================================================================

# Strict CSP for production
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'", "data:")
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# =================================================================
# PRODUCTION VALIDATION
# =================================================================

# Validate critical production settings
def validate_production_settings():
    """Validate that all critical production settings are properly configured"""
    errors = []
    
    if DEBUG:
        errors.append("DEBUG must be False in production")
    
    if SECRET_KEY == 'django-insecure-change-me-in-production':
        errors.append("SECRET_KEY must be changed from default value")
    
    if not ALLOWED_HOSTS or 'localhost' in ALLOWED_HOSTS:
        errors.append("ALLOWED_HOSTS must be configured with production domains")
    
    if not config('POSTGRES_PASSWORD', default=''):
        errors.append("POSTGRES_PASSWORD must be set")
    
    if errors:
        raise ValueError(f"Production configuration errors: {', '.join(errors)}")

# Run validation
validate_production_settings()
