akhshyganesh: Provide a very detailed report of this application for choice of library and the feature implemented in this make sure it is deep and clear about every line of this software totally, provide me file names, functions library names and reasons for each choice #codebase 

GitHub Copilot: # Comprehensive Technical Analysis Report: Production Django REST Framework SAAS Application

## Executive Summary

This is a production-ready Django REST Framework application designed for enterprise-level SAAS deployments with government-grade security standards. The application implements a comprehensive security framework with multi-layered authentication, authorization, and monitoring systems.

## Architecture Overview

### Core Framework Stack

#### **Django Framework (v4.2.16)**
- **File**: requirements.txt line 2
- **Choice Rationale**: Django 4.2 is the latest LTS (Long Term Support) version providing stability and security updates through April 2026
- **Security Benefits**: Built-in CSRF protection, SQL injection prevention, XSS protection headers

#### **Django REST Framework (v3.14.0)**
- **File**: requirements.txt line 3
- **Purpose**: API development framework for building RESTful services
- **Features**: Serialization, authentication, permissions, viewsets, and API documentation

#### **PostgreSQL Integration (psycopg2-binary v2.9.9)**
- **File**: requirements.txt line 7
- **Choice**: Production-grade database with ACID compliance
- **Configuration**: settings.py with `dj-database-url` for flexible connection string management

## Security Framework Analysis

### 1. Authentication System

#### **Multi-Factor Authentication (MFA)**
- **Library**: `pyotp==2.9.0` and `qrcode[pil]==7.4.2`
- **File**: requirements.txt lines 38-39
- **Implementation**: TOTP (Time-based One-Time Password) support
- **API Endpoints**: 
  - Setup: `POST /api/v1/auth/mfa/setup/`
  - Verification: `POST /api/v1/auth/mfa/verify/`

#### **Firebase Authentication Integration**
- **Library**: `firebase-admin==6.3.0`
- **File**: requirements.txt line 12
- **Purpose**: Enterprise SSO integration with Google Firebase
- **Configuration**: settings.py with Firebase credentials
- **API Endpoint**: `POST /api/v1/auth/firebase-login/`

#### **JWT Token Management**
- **Libraries**: 
  - `PyJWT==2.8.0` for token handling
  - `django-rest-knox==4.2.0` for secure token storage
- **File**: requirements.txt lines 10, 13
- **Security**: Knox provides token-based authentication with automatic expiration

#### **Cryptographic Security**
- **Library**: `cryptography>=41.0.0,<42.0.0`
- **File**: requirements.txt line 11
- **Purpose**: High-level cryptographic operations for secure token generation and encryption

### 2. Authorization System (RBAC/ABAC Hybrid)

#### **Permission Models Architecture**
- **File**: models.py
- **Components**:
  - **Permission Model**: Base permissions with `codename`, `name`, `permission_type`
  - **Role Model**: User roles with hierarchical inheritance
  - **UserRole Model**: Many-to-many relationship with expiration support
  - **PolicyRule Model**: ABAC rules engine with JSON attributes
  - **ResourcePermission Model**: Object-level permissions
  - **AuditLog Model**: Comprehensive security logging

#### **Permission Utility Functions**
- **File**: utils.py
- **Key Functions**:
  - `create_default_permissions()`: Bootstrap system permissions
  - `check_user_permission()`: Permission evaluation engine
  - `get_user_resources()`: Resource filtering based on permissions
  - `create_audit_log()`: Security event logging

#### **Guardian Integration**
- **Library**: `django-guardian==2.4.0`
- **File**: requirements.txt line 13
- **Purpose**: Object-level permissions for fine-grained access control

### 3. Security Middleware & Protection

#### **Brute Force Protection**
- **Library**: `django-axes==6.1.1`
- **File**: requirements.txt line 24
- **Configuration**: settings.py lines 308+
- **Features**:
  - Account lockout after 3 failed attempts
  - 2-hour cooldown period
  - IP-based tracking and whitelisting

#### **Rate Limiting**
- **Library**: `django-ratelimit==4.1.0`
- **File**: requirements.txt line 23
- **Implementation**: Built-in rate limiting without reverse proxy dependency
- **Configuration**: Different limits per endpoint type
  - Authentication: 10 requests/minute
  - API: 100 requests/minute
  - General: 200 requests/minute

#### **Content Security Policy (CSP)**
- **Library**: `django-csp==3.7`
- **File**: requirements.txt line 22
- **Configuration**: SECURITY.md lines 46+
- **Policy**: Strict CSP with `'self'` directives for all content types

#### **CORS Management**
- **Library**: `django-cors-headers==4.3.1`
- **File**: requirements.txt line 4
- **Purpose**: Cross-Origin Resource Sharing configuration for API access

### 4. Environment & Configuration Management

#### **Environment Variables**
- **Library**: `python-decouple==3.8`
- **File**: requirements.txt line 16
- **Configuration File**: .env.example
- **Security Variables**:
  - `SECRET_KEY`: Django secret key
  - `DEBUG`: Production debug setting
  - `ALLOWED_HOSTS`: Hostname restrictions
  - `CSRF_TRUSTED_ORIGINS`: CSRF protection origins

#### **Database URL Configuration**
- **Library**: `dj-database-url==2.1.0`
- **File**: requirements.txt line 8
- **Purpose**: Flexible database connection string parsing from environment

## Infrastructure & Deployment

### 1. Containerization

#### **Docker Configuration**
- **File**: Dockerfile
- **Base Image**: `python:3.11-slim-bullseye`
- **Security Features**:
  - Non-root user (`django:django`) for container security
  - Minimal system dependencies to reduce attack surface
  - Proper file permissions and ownership

#### **Production Optimizations**:
- Build-essential tools removed after Python package installation
- Separate directories for static files, media, and logs
- Health check endpoints for monitoring

### 2. Web Server Configuration

#### **Gunicorn WSGI Server**
- **Library**: `gunicorn==21.2.0`
- **File**: requirements.txt line 19
- **Configuration**: SECURITY.md lines 188+
- **Security Features**:
  - Dynamic worker scaling: `workers = cpu_count() * 2 + 1`
  - Request size limits: `limit_request_line = 4094`
  - Worker process isolation with automatic restarts
  - Comprehensive logging for security monitoring

#### **Static File Serving**
- **Library**: `whitenoise==6.6.0`
- **File**: requirements.txt line 18
- **Purpose**: Secure static file serving without separate web server
- **Benefits**: Simplified deployment architecture

### 3. Caching & Session Management

#### **Redis Integration**
- **Libraries**: `redis==5.0.1`, `django-redis==5.4.0`
- **File**: requirements.txt lines 44-45
- **Configuration**: settings.py
- **Uses**:
  - Session storage with secure cookie settings
  - Permission caching for performance
  - Rate limiting storage

### 4. Background Task Processing

#### **Celery Task Queue**
- **Libraries**: `celery==5.3.4`, `django-celery-beat==2.5.0`
- **File**: requirements.txt lines 47-48
- **Implementation**: tasks.py
- **Security Tasks**:
  - `generate_security_report()`: Daily security metrics compilation
  - Permission cleanup and maintenance
  - User account status monitoring

## Monitoring & Observability

### 1. Error Tracking

#### **Sentry Integration**
- **Library**: `sentry-sdk[django]==1.38.0`
- **File**: requirements.txt line 27
- **Configuration**: settings.py lines 340+
- **Features**: Real-time error tracking and performance monitoring

### 2. Comprehensive Logging

#### **Logging Configuration**
- **File**: settings.py lines 340+
- **Components**:
  - **File Handler**: Persistent log storage in `/app/logs/django.log`
  - **Console Handler**: Development and container logging
  - **Structured Logging**: Verbose format with timestamp, module, process info

#### **Security Audit Logging**
- **Model**: models.py - `AuditLog`
- **Function**: utils.py - `create_audit_log()`
- **Tracked Events**:
  - Permission grants/denials
  - Role assignments/revocations
  - Access attempts and results
  - Policy applications

### 3. API Documentation

#### **Swagger/OpenAPI Integration**
- **Library**: `drf-spectacular==0.26.5`
- **File**: requirements.txt line 29
- **Configuration**: settings.py lines 308+
- **Features**:
  - Interactive API documentation at `/api/docs/`
  - Automatic schema generation
  - Security scheme documentation

## Database Architecture

### 1. Migration System

#### **Initial Migration**
- **File**: 0001_initial.py
- **Tables Created**:
  - `permissions`: Base permission definitions
  - `roles`: Role hierarchy with metadata
  - `user_roles`: User-role assignments with expiration
  - `policy_rules`: ABAC rule engine storage
  - `resource_permissions`: Object-level permissions
  - `audit_logs`: Security event logging

#### **Database Indexes**
- **Performance Optimization**: 
  - Composite indexes on frequently queried fields
  - `roles_name_a29c01_idx`: Role name lookups
  - `audit_logs_user_id_88267f_idx`: User-specific audit trails
  - `permissions_codenam_712f4a_idx`: Permission code lookups

### 2. Database Security

#### **Connection Security**
- **Configuration**: SECURITY.md and README.md lines 266+
- **Features**:
  - Dedicated database user with minimal privileges
  - Connection pooling and timeout configuration
  - Encrypted connections (configurable)

## Testing & Quality Assurance

### 1. Test Configuration

#### **Test Settings**
- **File**: test_settings.py
- **Optimizations**:
  - In-memory SQLite for fast test execution
  - Disabled migrations for performance
  - Dummy cache backend
  - Weak password hashing for speed
  - Console email backend

#### **Test Coverage**
- **Library**: Coverage tools integrated
- **Commands**: `coverage run --source='.' manage.py test`

## Security Compliance Features

### 1. Government-Level Security Standards

#### **Password Policy**
- **Requirements**: 12+ character minimum with complexity rules
- **History**: Prevents reuse of last 5 passwords
- **Validation**: Custom validators for enterprise compliance

#### **Session Security**
- **Configuration**: SECURITY.md lines 46+
- **Settings**:
  - `SESSION_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_AGE = 3600` (1 hour)
  - `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`
  - `SESSION_COOKIE_SAMESITE = 'Strict'`

#### **CSRF Protection**
- **Enhanced Configuration**:
  - `CSRF_COOKIE_HTTPONLY = True`
  - `CSRF_COOKIE_SAMESITE = 'Strict'`
  - `CSRF_USE_SESSIONS = True`

### 2. Compliance Reporting

#### **Audit Trail Requirements**
- **Model**: Complete audit logging with immutable records
- **Fields**: User, action, timestamp, IP address, user agent, success/failure
- **Retention**: Configurable retention periods for compliance

#### **Security Incident Response**
- **File**: SECURITY.md lines 123+
- **Automated Detection**: SQL injection, XSS attempts, scanning tools
- **Response Procedures**: Account lockout, IP blocking, admin notifications

## Performance Optimization

### 1. Caching Strategy

#### **Permission Caching**
- **Implementation**: Redis-based permission result caching
- **Invalidation**: Automatic cache invalidation on permission changes
- **Performance**: Reduces database queries for permission checks

#### **Static File Optimization**
- **WhiteNoise**: Efficient static file serving with compression
- **CDN Ready**: Headers configured for CDN integration

### 2. Database Optimization

#### **Query Optimization**
- **Indexes**: Strategic indexing on frequently queried fields
- **Select Related**: Optimized ORM queries to reduce N+1 problems
- **Connection Pooling**: Efficient database connection management

## Development & Deployment Features

### 1. Development Tools

#### **Filter Integration**
- **Library**: `django-filter==23.5`
- **File**: requirements.txt line 42
- **Purpose**: Advanced filtering for API endpoints

#### **Date Utilities**
- **Library**: `python-dateutil==2.8.2`
- **File**: requirements.txt line 49
- **Purpose**: Enhanced date/time handling for time-based permissions

### 2. Production Deployment

#### **Health Checks**
- **Endpoint**: `/health/`
- **Monitoring**: Application health and dependency status
- **Integration**: Container orchestration support

#### **Security Testing**
- **Endpoint**: `/security-test/`
- **Purpose**: Verify security header configuration
- **Compliance**: Automated security validation

## Configuration Management

### 1. Environment-Specific Settings

#### **Production Configuration**
- **File**: settings.py
- **Environment Detection**: `DJANGO_ENV` variable
- **Security Defaults**: Production-safe defaults with environment overrides

#### **Development Overrides**
- **Debug Mode**: Configurable via environment
- **Logging Levels**: Environment-specific log configuration
- **Database**: Flexible database configuration via URL

### 2. Security Configuration

#### **IP Whitelisting**
- **Admin Access**: Configurable IP whitelist for admin interface
- **Environment Variable**: `ADMIN_ALLOWED_IPS`
- **Default**: Localhost only for security

#### **Rate Limiting Configuration**
- **Granular Control**: Different limits per endpoint type
- **IP-Based**: Per-IP rate limiting
- **Configurable**: Environment-based rate limit configuration

## Key Security Recommendations Implemented

1. **Defense in Depth**: Multiple security layers from network to application level
2. **Principle of Least Privilege**: Minimal permissions by default
3. **Zero Trust Architecture**: Every request authenticated and authorized
4. **Comprehensive Monitoring**: Full audit trail and real-time monitoring
5. **Incident Response**: Automated detection and response capabilities
6. **Compliance Ready**: Government-level security standards implementation

## Conclusion

This Django REST Framework application represents a comprehensive enterprise-grade SAAS platform with military-level security implementation. Every library choice serves a specific security, performance, or functionality purpose, creating a robust foundation for production deployment. The hybrid RBAC/ABAC authorization system, comprehensive audit logging, and multi-layered security approach make it suitable for high-security environments including government and financial sector deployments.

The architecture emphasizes security-first design principles while maintaining high performance and scalability through strategic use of caching, background processing, and optimized database design. The comprehensive documentation and configuration management ensure maintainable and auditable deployments.

akhshyganesh: okay now I want to create roles and add persmission for each of them, how should my API request look like #codebase 

GitHub Copilot: Based on the codebase analysis, here are the API requests for creating roles and assigning permissions:

## Creating Roles

### 1. Create a New Role

```http
POST /api/v1/permissions/roles/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Project Manager",
    "description": "Can manage projects and team members",
    "role_type": "organizational",
    "parent_role": null,
    "attributes": {
        "department": "Engineering",
        "level": "mid"
    },
    "max_users": 10,
    "expires_at": null,
    "is_active": true
}
```

**Role Types Available:**
- `system` - System Role
- `organizational` - Organizational Role  
- `functional` - Functional Role
- `custom` - Custom Role (default)

## Assigning Permissions to Roles

### 2. Assign Permission to Role

```http
POST /api/v1/permissions/roles/{role_id}/assign-permission/
Authorization: Bearer <token>
Content-Type: application/json

{
    "permission_id": "permission-uuid-here"
}
```

### 3. Get Available Permissions (to find permission IDs)

```http
GET /api/v1/permissions/permissions/
Authorization: Bearer <token>
```

**Response includes permissions like:**
```json
{
    "results": [
        {
            "id": "uuid-here",
            "name": "View User",
            "codename": "view_user",
            "permission_type": "resource"
        },
        {
            "id": "uuid-here", 
            "name": "Add User",
            "codename": "add_user",
            "permission_type": "action"
        }
    ]
}
```

## Complete Example Workflow

### Step 1: Create Role
```http
POST /api/v1/permissions/roles/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Content Editor",
    "description": "Can create and edit content",
    "role_type": "functional",
    "is_active": true
}
```

### Step 2: Get Role ID from Response
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Content Editor",
    "description": "Can create and edit content",
    "role_type": "functional",
    "is_active": true
}
```

### Step 3: Assign Multiple Permissions
```http
POST /api/v1/permissions/roles/550e8400-e29b-41d4-a716-446655440000/assign-permission/
Authorization: Bearer <token>
Content-Type: application/json

{
    "permission_id": "view-user-permission-uuid"
}
```

```http
POST /api/v1/permissions/roles/550e8400-e29b-41d4-a716-446655440000/assign-permission/
Authorization: Bearer <token>
Content-Type: application/json

{
    "permission_id": "api-access-permission-uuid"
}
```

## Alternative: Bulk Role Creation with Permissions

You can also use the management command to create default roles:

```bash
python manage.py create_default_permissions
```

This creates the following default roles with their permissions:

1. **Super Administrator** - Full system access
2. **Administrator** - Administrative access
3. **Manager** - Management access  
4. **Employee** - Standard employee access
5. **Client** - Client access
6. **Guest** - Limited guest access

## Verify Role Permissions

### Get Role with Permissions
```http
GET /api/v1/permissions/roles/{role_id}/
Authorization: Bearer <token>
```

### Get Role Permissions List
```http
GET /api/v1/permissions/roles/{role_id}/permissions/
Authorization: Bearer <token>
```

## Required Permissions

To perform these operations, your user needs:
- `add_role` - To create roles
- `change_role` - To assign/revoke permissions from roles
- `view_role` - To view roles
- `view_permission` - To view available permissions

The system uses the `DynamicPermission` class to enforce these permissions through the RBAC/ABAC system.

akhshyganesh: how to create other permissions and also how to set this requirements in API ? 

GitHub Copilot: # Creating Custom Permissions and Setting API Requirements

Based on the codebase, here's how to create custom permissions and configure API requirements:

## 1. Creating Custom Permissions

### Method A: Using Django Management Command

````python
from django.core.management.base import BaseCommand
from apps.permissions.models import Permission

class Command(BaseCommand):
    help = 'Create custom permissions'

    def handle(self, *args, **options):
        custom_permissions = [
            {
                'name': 'Can View Dashboard',
                'codename': 'view_dashboard',
                'permission_type': 'feature',
                'description': 'Access to main dashboard'
            },
            {
                'name': 'Can Export Data',
                'codename': 'export_data',
                'permission_type': 'action',
                'description': 'Export data to CSV/Excel'
            },
            {
                'name': 'Can Manage Billing',
                'codename': 'manage_billing',
                'permission_type': 'feature',
                'description': 'Access billing and subscription management'
            },
            {
                'name': 'Can Access Reports',
                'codename': 'access_reports',
                'permission_type': 'feature',
                'description': 'View and generate reports'
            },
            {
                'name': 'Can Delete Records',
                'codename': 'delete_records',
                'permission_type': 'action',
                'description': 'Delete system records'
            }
        ]

        for perm_data in custom_permissions:
            permission, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults=perm_data
            )
            if created:
                self.stdout.write(f"Created permission: {permission.name}")
            else:
                self.stdout.write(f"Permission already exists: {permission.name}")
````

### Method B: Using API Endpoint

```http
POST /api/v1/permissions/permissions/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Can Manage API Keys",
    "codename": "manage_api_keys",
    "permission_type": "feature",
    "description": "Create and manage API keys",
    "is_active": true,
    "attributes": {
        "category": "security",
        "risk_level": "high"
    }
}
```

### Method C: Using Django Admin or Shell

````python
# In Django shell: python manage.py shell
from apps.permissions.models import Permission

# Create individual permissions
permission = Permission.objects.create(
    name="Can Access Advanced Features",
    codename="access_advanced_features",
    permission_type="feature",
    description="Access to premium features"
)

# Bulk create permissions
permissions_data = [
    {
        'name': 'Can View Analytics',
        'codename': 'view_analytics',
        'permission_type': 'feature'
    },
    {
        'name': 'Can Moderate Content',
        'codename': 'moderate_content',
        'permission_type': 'action'
    }
]

for perm_data in permissions_data:
    Permission.objects.get_or_create(
        codename=perm_data['codename'],
        defaults=perm_data
    )
````

## 2. Permission Types Available

Based on the model, you can create permissions with these types:

- **`resource`** - Access to specific resources (users, projects, etc.)
- **`action`** - Specific actions (create, edit, delete, export)
- **`feature`** - Feature-level access (dashboard, reports, billing)
- **`api`** - API endpoint access
- **`admin`** - Administrative functions
- **`system`** - System-level operations

## 3. Setting API Requirements with Permissions

### Method A: Using Custom Permission Classes

````python
from rest_framework.permissions import BasePermission
from apps.permissions.utils import check_user_permission

class HasFeaturePermission(BasePermission):
    """
    Custom permission to check if user has specific feature permission
    """
    required_permission = None
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        if self.required_permission:
            return check_user_permission(
                request.user, 
                self.required_permission, 
                request=request
            )
        return True

class CanViewDashboard(HasFeaturePermission):
    required_permission = 'view_dashboard'

class CanExportData(HasFeaturePermission):
    required_permission = 'export_data'

class CanManageBilling(HasFeaturePermission):
    required_permission = 'manage_billing'

class CanAccessReports(HasFeaturePermission):
    required_permission = 'access_reports'
````

### Method B: Using the Existing DynamicPermission Class

````python
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.permissions.permissions import DynamicPermission
from apps.permissions.utils import check_user_permission

class DashboardViewSet(ModelViewSet):
    permission_classes = [DynamicPermission]
    required_permissions = {
        'list': ['view_dashboard'],
        'retrieve': ['view_dashboard'],
        'create': ['manage_dashboard'],
        'update': ['manage_dashboard'],
        'destroy': ['manage_dashboard'],
        'export_data': ['export_data'],
        'analytics': ['view_analytics']
    }
    
    @action(detail=False, methods=['get'])
    def export_data(self, request):
        # This will automatically check 'export_data' permission
        # due to required_permissions mapping above
        return Response({'message': 'Exporting data...'})
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        # This will check 'view_analytics' permission
        return Response({'analytics': 'data'})
````

### Method C: Using Decorators for Function-Based Views

````python
from functools import wraps
from django.http import JsonResponse
from apps.permissions.utils import check_user_permission

def require_permission(permission_codename):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            if not check_user_permission(request.user, permission_codename, request=request):
                return JsonResponse({'error': 'Permission denied'}, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage in views:
@require_permission('view_dashboard')
def dashboard_view(request):
    return JsonResponse({'dashboard': 'data'})

@require_permission('export_data')
def export_view(request):
    return JsonResponse({'export': 'starting'})
````

## 4. Advanced Permission Configuration

### Resource-Level Permissions

````python
# Create resource-specific permissions
from apps.permissions.models import ResourcePermission

# Grant user permission to specific resource
ResourcePermission.objects.create(
    user=user,
    permission=permission,
    resource_type='project',
    resource_id=project.id,
    granted_by=admin_user
)
````

### Policy-Based Permissions (ABAC)

````python
# Create policy rules for attribute-based access
from apps.permissions.models import PolicyRule

# Example: Only managers can access billing in business hours
PolicyRule.objects.create(
    name="Billing Access Policy",
    rule_type="time_based",
    conditions={
        "user_role": "manager",
        "time_range": {
            "start": "09:00",
            "end": "17:00"
        },
        "weekdays": [1, 2, 3, 4, 5]  # Monday to Friday
    },
    permissions=["manage_billing"],
    is_active=True
)
````

## 5. API Endpoints for Permission Management

### Get All Permissions
```http
GET /api/v1/permissions/permissions/
Authorization: Bearer <token>
```

### Create New Permission
```http
POST /api/v1/permissions/permissions/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Can Access Premium Features",
    "codename": "access_premium",
    "permission_type": "feature",
    "description": "Access to premium subscription features",
    "attributes": {
        "subscription_tier": "premium",
        "category": "subscription"
    }
}
```

### Assign Permission to User
```http
POST /api/v1/permissions/users/{user_id}/assign-permission/
Authorization: Bearer <token>
Content-Type: application/json

{
    "permission_id": "permission-uuid-here",
    "expires_at": "2024-12-31T23:59:59Z"
}
```

### Check User Permission
```http
GET /api/v1/permissions/users/{user_id}/check-permission/?permission=view_dashboard
Authorization: Bearer <token>
```

## 6. Testing Permissions

### Unit Test Example

````python
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.permissions.models import Permission, Role
from apps.permissions.utils import check_user_permission

User = get_user_model()

class CustomPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.permission = Permission.objects.create(
            name='Can View Dashboard',
            codename='view_dashboard',
            permission_type='feature'
        )
        
        self.role = Role.objects.create(
            name='Dashboard User',
            description='Can access dashboard'
        )
        
    def test_permission_assignment(self):
        # Assign permission to role
        self.role.permissions.add(self.permission)
        
        # Assign role to user
        self.user.roles.add(self.role)
        
        # Test permission check
        has_permission = check_user_permission(
            self.user, 
            'view_dashboard'
        )
        
        self.assertTrue(has_permission)
````

## 7. Permission Hierarchy Example

```python
# Create hierarchical permissions
parent_permission = Permission.objects.create(
    name="Can Manage Users",
    codename="manage_users",
    permission_type="resource"
)

child_permissions = [
    {
        'name': 'Can View Users',
        'codename': 'view_users',
        'permission_type': 'resource',
        'parent': parent_permission
    },
    {
        'name': 'Can Create Users', 
        'codename': 'create_users',
        'permission_type': 'action',
        'parent': parent_permission
    }
]

for perm_data in child_permissions:
    Permission.objects.create(**perm_data)
```

This comprehensive approach allows you to create granular permissions and enforce them at the API level using the existing RBAC/ABAC system in your Django application.

akhshyganesh: where all can I use redis and celery in my application, mainly this application is going to be used for django restframework only, where all can this help me and what else of techniques and features are present in this application

GitHub Copilot: # Redis and Celery Integration Guide for Django REST Framework Application

Based on your codebase analysis, here's a comprehensive guide on where and how to use Redis and Celery in your DRF application:

## 1. Redis Usage Areas

### A. Session Management
````python
# ...existing code...
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 3600  # 1 hour
# ...existing code...
````

### B. Permission Caching
````python
# filepath: apps/permissions/cache.py
import redis
from django.core.cache import cache
from django.conf import settings
import json

class PermissionCache:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.cache_timeout = 3600  # 1 hour
    
    def get_user_permissions(self, user_id):
        """Get cached user permissions"""
        cache_key = f"user_perms:{user_id}"
        cached_perms = cache.get(cache_key)
        
        if cached_perms:
            return json.loads(cached_perms)
        return None
    
    def set_user_permissions(self, user_id, permissions):
        """Cache user permissions"""
        cache_key = f"user_perms:{user_id}"
        cache.set(cache_key, json.dumps(permissions), self.cache_timeout)
    
    def invalidate_user_permissions(self, user_id):
        """Invalidate user permission cache"""
        cache_key = f"user_perms:{user_id}"
        cache.delete(cache_key)
    
    def get_role_permissions(self, role_id):
        """Get cached role permissions"""
        cache_key = f"role_perms:{role_id}"
        return cache.get(cache_key)
    
    def set_role_permissions(self, role_id, permissions):
        """Cache role permissions"""
        cache_key = f"role_perms:{role_id}"
        cache.set(cache_key, permissions, self.cache_timeout)
````

### C. Rate Limiting Storage
````python
from django.core.cache import cache
from django.http import JsonResponse
import time

class RedisRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # API rate limiting
        if request.path.startswith('/api/'):
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit:{client_ip}"
            
            # Get current request count
            current_requests = cache.get(cache_key, 0)
            
            if current_requests >= 100:  # 100 requests per minute
                return JsonResponse({
                    'error': 'Rate limit exceeded',
                    'retry_after': 60
                }, status=429)
            
            # Increment counter
            cache.set(cache_key, current_requests + 1, 60)
        
        return self.get_response(request)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
````

### D. API Response Caching
````python
from django.core.cache import cache
from django.http import JsonResponse
from functools import wraps
import json
import hashlib

def cache_api_response(timeout=300):
    """Cache API responses for specified timeout"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Create cache key from request
            cache_key = f"api_response:{request.path}:{request.GET.urlencode()}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response:
                return JsonResponse(cached_response)
            
            # Get fresh response
            response = view_func(request, *args, **kwargs)
            
            # Cache successful responses
            if response.status_code == 200:
                cache.set(cache_key, response.data, timeout)
            
            return response
        return wrapper
    return decorator

# Usage example:
@cache_api_response(timeout=600)  # Cache for 10 minutes
def get_dashboard_data(request):
    # Expensive data processing
    return JsonResponse({'dashboard': 'data'})
````

### E. Real-time Notifications Queue
````python
import redis
import json
from django.conf import settings

class NotificationQueue:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
    
    def push_notification(self, user_id, notification_data):
        """Push notification to user's queue"""
        queue_key = f"notifications:{user_id}"
        notification = {
            'id': notification_data['id'],
            'type': notification_data['type'],
            'message': notification_data['message'],
            'timestamp': notification_data['timestamp'],
            'read': False
        }
        
        # Add to list (FIFO queue)
        self.redis_client.lpush(queue_key, json.dumps(notification))
        
        # Keep only last 100 notifications
        self.redis_client.ltrim(queue_key, 0, 99)
        
        # Set expiration (30 days)
        self.redis_client.expire(queue_key, 2592000)
    
    def get_notifications(self, user_id, limit=20):
        """Get user notifications"""
        queue_key = f"notifications:{user_id}"
        notifications = self.redis_client.lrange(queue_key, 0, limit-1)
        
        return [json.loads(notif) for notif in notifications]
    
    def mark_read(self, user_id, notification_id):
        """Mark notification as read"""
        queue_key = f"notifications:{user_id}"
        notifications = self.redis_client.lrange(queue_key, 0, -1)
        
        updated_notifications = []
        for notif in notifications:
            notif_data = json.loads(notif)
            if notif_data['id'] == notification_id:
                notif_data['read'] = True
            updated_notifications.append(json.dumps(notif_data))
        
        # Replace the entire list
        if updated_notifications:
            self.redis_client.delete(queue_key)
            for notif in reversed(updated_notifications):
                self.redis_client.lpush(queue_key, notif)
````

## 2. Celery Task Areas

### A. Security and Audit Tasks
````python
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.permissions.models import AuditLog
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

@shared_task
def generate_security_report():
    """Generate daily security report"""
    yesterday = timezone.now() - timedelta(days=1)
    
    # Get security events
    failed_logins = AuditLog.objects.filter(
        action='login_failed',
        timestamp__gte=yesterday
    ).count()
    
    suspicious_activities = AuditLog.objects.filter(
        action__in=['permission_denied', 'unauthorized_access'],
        timestamp__gte=yesterday
    ).count()
    
    report = {
        'date': yesterday.date(),
        'failed_logins': failed_logins,
        'suspicious_activities': suspicious_activities,
        'total_events': failed_logins + suspicious_activities
    }
    
    logger.info(f"Security report generated: {report}")
    return report

@shared_task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    from django.contrib.sessions.models import Session
    
    expired_sessions = Session.objects.filter(
        expire_date__lt=timezone.now()
    )
    
    count = expired_sessions.count()
    expired_sessions.delete()
    
    logger.info(f"Cleaned up {count} expired sessions")
    return count

@shared_task
def monitor_suspicious_activity(user_id, activity_type, metadata):
    """Monitor and respond to suspicious activities"""
    user = User.objects.get(id=user_id)
    
    # Check for patterns
    recent_activities = AuditLog.objects.filter(
        user=user,
        action=activity_type,
        timestamp__gte=timezone.now() - timedelta(minutes=5)
    ).count()
    
    if recent_activities > 10:  # Threshold for suspicious activity
        # Lock account temporarily
        user.is_active = False
        user.save()
        
        # Send alert to admins
        send_security_alert.delay(
            user_id=user_id,
            alert_type='account_locked',
            reason='Suspicious activity detected'
        )
        
        logger.warning(f"Account {user.username} locked due to suspicious activity")
````

### B. Email and Communication Tasks
````python
from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(user_id):
    """Send welcome email to new users"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = 'Welcome to Our Platform'
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'login_url': f"{settings.FRONTEND_URL}/login"
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email: {str(e)}")
        return False

@shared_task
def send_password_reset_email(user_id, reset_token):
    """Send password reset email"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
        
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = 'Password Reset Request'
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message
        )
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
        return False

@shared_task
def send_bulk_notifications(user_ids, notification_type, message):
    """Send bulk notifications to multiple users"""
    from apps.notifications.redis_queue import NotificationQueue
    
    notification_queue = NotificationQueue()
    
    for user_id in user_ids:
        notification_data = {
            'id': f"{notification_type}_{user_id}_{timezone.now().timestamp()}",
            'type': notification_type,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        
        notification_queue.push_notification(user_id, notification_data)
    
    logger.info(f"Sent bulk notification to {len(user_ids)} users")
    return len(user_ids)
````

### C. Data Processing Tasks
````python
from celery import shared_task
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import csv
import os

@shared_task
def generate_user_analytics():
    """Generate user analytics report"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_last_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    analytics = {
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': total_users - active_users,
        'new_users_last_week': new_users_last_week,
        'generated_at': timezone.now().isoformat()
    }
    
    return analytics

@shared_task
def export_user_data(user_id, export_format='csv'):
    """Export user data for GDPR compliance"""
    from django.contrib.auth import get_user_model
    from apps.permissions.models import AuditLog
    
    User = get_user_model()
    user = User.objects.get(id=user_id)
    
    # Collect user data
    user_data = {
        'basic_info': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None
        },
        'audit_logs': list(AuditLog.objects.filter(user=user).values(
            'action', 'timestamp', 'ip_address', 'user_agent'
        ))
    }
    
    # Generate export file
    export_path = f"/tmp/user_export_{user_id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(export_path, 'w') as f:
        json.dump(user_data, f, indent=2, default=str)
    
    # Send email with download link (implement based on your file storage)
    send_data_export_email.delay(user_id, export_path)
    
    return export_path

@shared_task
def cleanup_old_audit_logs():
    """Clean up audit logs older than retention period"""
    from apps.permissions.models import AuditLog
    
    retention_days = 90  # Keep logs for 90 days
    cutoff_date = timezone.now() - timedelta(days=retention_days)
    
    old_logs = AuditLog.objects.filter(timestamp__lt=cutoff_date)
    count = old_logs.count()
    old_logs.delete()
    
    logger.info(f"Cleaned up {count} old audit logs")
    return count
````

### D. API Rate Limiting and Monitoring
````python
from celery import shared_task
from django.core.cache import cache
from django.contrib.auth import get_user_model
import json

@shared_task
def monitor_api_usage():
    """Monitor API usage patterns"""
    # Get API usage statistics from Redis
    api_stats = {}
    
    # This would collect stats from your rate limiting cache
    for endpoint in ['/api/v1/auth/', '/api/v1/users/', '/api/v1/permissions/']:
        cache_pattern = f"rate_limit:*:{endpoint}*"
        # Implement Redis pattern matching to get usage stats
        # This is a simplified example
        usage_count = cache.get(f"api_usage:{endpoint}", 0)
        api_stats[endpoint] = usage_count
    
    return api_stats

@shared_task
def detect_api_abuse():
    """Detect API abuse patterns"""
    # Monitor for suspicious API usage
    suspicious_ips = []
    
    # Check for IPs with excessive requests
    # This would analyze your rate limiting data
    
    for ip in suspicious_ips:
        # Block suspicious IPs
        cache.set(f"blocked_ip:{ip}", True, 3600)  # Block for 1 hour
    
    return len(suspicious_ips)
````

## 3. Celery Beat Schedule Configuration

````python
from celery.schedules import crontab

# ...existing code...

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    # Security tasks
    'generate-security-report': {
        'task': 'apps.security.tasks.generate_security_report',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
    },
    'cleanup-expired-sessions': {
        'task': 'apps.security.tasks.cleanup_expired_sessions',
        'schedule': crontab(minute=0),  # Every hour
    },
    'cleanup-old-audit-logs': {
        'task': 'apps.analytics.tasks.cleanup_old_audit_logs',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    
    # Analytics tasks
    'generate-user-analytics': {
        'task': 'apps.analytics.tasks.generate_user_analytics',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
    },
    
    # Monitoring tasks
    'monitor-api-usage': {
        'task': 'apps.monitoring.tasks.monitor_api_usage',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'detect-api-abuse': {
        'task': 'apps.monitoring.tasks.detect_api_abuse',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
}

CELERY_TIMEZONE = 'UTC'
# ...existing code...
````

## 4. Advanced Techniques and Features in Your Application

### A. Circuit Breaker Pattern for External APIs
````python
import time
from functools import wraps
from django.core.cache import cache

class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            circuit_key = f"circuit_breaker:{func.__name__}"
            
            # Check circuit state
            circuit_state = cache.get(circuit_key, {'failures': 0, 'last_failure': 0, 'state': 'closed'})
            
            if circuit_state['state'] == 'open':
                if time.time() - circuit_state['last_failure'] < self.recovery_timeout:
                    raise Exception("Circuit breaker is OPEN")
                else:
                    circuit_state['state'] = 'half-open'
            
            try:
                result = func(*args, **kwargs)
                # Success - close circuit
                circuit_state = {'failures': 0, 'last_failure': 0, 'state': 'closed'}
                cache.set(circuit_key, circuit_state, 3600)
                return result
                
            except Exception as e:
                # Failure - update circuit state
                circuit_state['failures'] += 1
                circuit_state['last_failure'] = time.time()
                
                if circuit_state['failures'] >= self.failure_threshold:
                    circuit_state['state'] = 'open'
                
                cache.set(circuit_key, circuit_state, 3600)
                raise e
                
        return wrapper
````

### B. Distributed Locking with Redis
````python
import redis
import time
import uuid
from contextlib import contextmanager

class DistributedLock:
    def __init__(self, key, timeout=10, redis_client=None):
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.redis_client = redis_client or redis.Redis.from_url(settings.REDIS_URL)
        self.identifier = str(uuid.uuid4())
    
    @contextmanager
    def acquire(self):
        try:
            if self._acquire_lock():
                yield
            else:
                raise Exception("Could not acquire lock")
        finally:
            self._release_lock()
    
    def _acquire_lock(self):
        end_time = time.time() + self.timeout
        
        while time.time() < end_time:
            if self.redis_client.set(self.key, self.identifier, nx=True, ex=self.timeout):
                return True
            time.sleep(0.001)
        
        return False
    
    def _release_lock(self):
        # Lua script to safely release lock
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        self.redis_client.eval(lua_script, 1, self.key, self.identifier)

# Usage:
@shared_task
def process_unique_task(task_id):
    lock = DistributedLock(f"unique_task:{task_id}")
    
    with lock.acquire():
        # This ensures only one instance of this task runs at a time
        # for the same task_id
        process_task_logic(task_id)
````

### C. Event Sourcing Pattern
````python
from django.db import models
import json
import uuid

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    aggregate_id = models.UUIDField()
    event_type = models.CharField(max_length=100)
    event_data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['aggregate_id', 'version']),
            models.Index(fields=['event_type', 'timestamp']),
        ]

class EventStore:
    @staticmethod
    def save_event(aggregate_id, event_type, event_data):
        # Get current version
        last_event = Event.objects.filter(
            aggregate_id=aggregate_id
        ).order_by('-version').first()
        
        version = (last_event.version + 1) if last_event else 1
        
        event = Event.objects.create(
            aggregate_id=aggregate_id,
            event_type=event_type,
            event_data=event_data,
            version=version
        )
        
        # Trigger event processing
        process_event.delay(event.id)
        
        return event
    
    @staticmethod
    def get_events(aggregate_id, from_version=None):
        queryset = Event.objects.filter(aggregate_id=aggregate_id)
        
        if from_version:
            queryset = queryset.filter(version__gte=from_version)
        
        return queryset.order_by('version')

@shared_task
def process_event(event_id):
    """Process events asynchronously"""
    event = Event.objects.get(id=event_id)
    
    # Route to appropriate handler based on event type
    handlers = {
        'user_registered': handle_user_registered,
        'permission_granted': handle_permission_granted,
        'role_assigned': handle_role_assigned,
    }
    
    handler = handlers.get(event.event_type)
    if handler:
        handler(event)
````

## 5. WebSocket Integration with Redis
````python
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import redis

class NotificationConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.user_id = None
    
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.group_name = f"user_{self.user_id}"
        
        # Join user group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send any pending notifications
        await self.send_pending_notifications()
    
    async def disconnect(self, close_code):
        # Leave user group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
    
    async def send_pending_notifications(self):
        """Send any pending notifications from Redis"""
        queue_key = f"notifications:{self.user_id}"
        notifications = self.redis_client.lrange(queue_key, 0, 9)  # Get last 10
        
        for notification in notifications:
            await self.send(text_data=notification.decode())
    
    async def notification_message(self, event):
        """Handle notification from group"""
        await self.send(text_data=json.dumps(event['message']))
````

## 6. API Response Optimization with Redis
````python
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.decorators import action
import hashlib
import json

class CachedAPIViewMixin:
    cache_timeout = 300  # 5 minutes default
    
    def get_cache_key(self, request, *args, **kwargs):
        """Generate cache key for request"""
        key_parts = [
            self.__class__.__name__,
            request.path,
            request.GET.urlencode(),
            str(request.user.id) if request.user.is_authenticated else 'anonymous'
        ]
        key = ':'.join(key_parts)
        return hashlib.md5(key.encode()).hexdigest()
    
    def get_cached_response(self, request, *args, **kwargs):
        """Get cached response if available"""
        cache_key = self.get_cache_key(request, *args, **kwargs)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        return None
    
    def cache_response(self, request, response, *args, **kwargs):
        """Cache response data"""
        if response.status_code == 200:
            cache_key = self.get_cache_key(request, *args, **kwargs)
            cache.set(cache_key, response.data, self.cache_timeout)
    
    def list(self, request, *args, **kwargs):
        # Try to get cached response
        cached_response = self.get_cached_response(request, *args, **kwargs)
        if cached_response:
            return cached_response
        
        # Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Cache the response
        self.cache_response(request, response, *args, **kwargs)
        
        return response
````

This comprehensive integration of Redis and Celery provides your DRF application with:

1. **High Performance**: Caching, session management, and background processing
2. **Scalability**: Distributed task processing and caching
3. **Real-time Features**: WebSocket support and notifications
4. **Security**: Rate limiting, session management, and monitoring
5. **Reliability**: Circuit breakers, distributed locks, and error handling
6. **Analytics**: Background data processing and reporting
7. **Compliance**: Audit log management and data export capabilities

These features make your application production-ready for enterprise-level deployments with government-grade security and performance requirements.


akhshyganesh: Provide me more tips and reusable code logics from this codebase with which my future development becomes handy #codebase 

GitHub Copilot: # Reusable Code Patterns and Development Tips from Your Codebase

Based on your comprehensive Django REST Framework SAAS application, here are powerful reusable patterns and tips for future development:

## 1. Advanced Permission System Patterns

### A. Reusable Permission Checker Mixin
```python
from django.core.exceptions import PermissionDenied
from apps.permissions.utils import check_user_permission
from rest_framework.response import Response

class PermissionRequiredMixin:
    """Reusable mixin for views requiring specific permissions"""
    required_permissions = {}  # {'action': ['permission1', 'permission2']}
    
    def check_permissions(self, request):
        super().check_permissions(request)
        
        action = self.action or 'default'
        permissions = self.required_permissions.get(action, [])
        
        for permission in permissions:
            if not check_user_permission(request.user, permission, request=request):
                raise PermissionDenied(f"Missing permission: {permission}")
    
    def get_allowed_actions(self, request):
        """Get list of allowed actions for current user"""
        allowed_actions = []
        
        for action, permissions in self.required_permissions.items():
            if all(check_user_permission(request.user, perm, request=request) 
                   for perm in permissions):
                allowed_actions.append(action)
        
        return allowed_actions

# Usage:
class DocumentViewSet(PermissionRequiredMixin, ModelViewSet):
    required_permissions = {
        'list': ['view_document'],
        'retrieve': ['view_document'],
        'create': ['add_document'],
        'update': ['change_document'],
        'destroy': ['delete_document'],
        'share': ['share_document'],
        'publish': ['publish_document']
    }
```

### B. Dynamic Permission Decorator
```python
from functools import wraps
from django.http import JsonResponse
from apps.permissions.utils import check_user_permission

def permission_required(permissions=None, resource_type=None):
    """
    Advanced permission decorator with resource-level checking
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({'error': 'Authentication required'}, status=401)
            
            # Check basic permissions
            for permission in (permissions or []):
                if not check_user_permission(request.user, permission, request=request):
                    return JsonResponse({
                        'error': f'Permission denied: {permission}',
                        'required_permissions': permissions
                    }, status=403)
            
            # Check resource-level permissions if resource_type provided
            if resource_type and 'pk' in kwargs:
                resource_id = kwargs['pk']
                if not check_user_permission(
                    request.user, 
                    f"access_{resource_type}", 
                    resource_type=resource_type,
                    resource_id=resource_id,
                    request=request
                ):
                    return JsonResponse({
                        'error': f'No access to {resource_type} {resource_id}'
                    }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

# Usage:
@permission_required(['view_reports', 'export_data'])
def export_report(request):
    return JsonResponse({'status': 'exporting'})

@permission_required(['view_project'], resource_type='project')
def project_detail(request, pk):
    return JsonResponse({'project_id': pk})
```

## 2. Smart Caching Patterns

### A. Multi-Level Cache System
```python
import json
import hashlib
from django.core.cache import cache
from django.conf import settings
import redis

class SmartCacheManager:
    """Multi-level caching with automatic invalidation"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL)
        self.default_timeout = 3600
    
    def get_cache_key(self, prefix, *args, **kwargs):
        """Generate consistent cache keys"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        
        key_string = ':'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def cached_result(self, key_prefix, timeout=None):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self.get_cache_key(key_prefix, *args, **kwargs)
                
                # Try to get from cache
                result = cache.get(cache_key)
                if result is not None:
                    return result
                
                # Get fresh result
                result = func(*args, **kwargs)
                
                # Cache the result
                cache.set(cache_key, result, timeout or self.default_timeout)
                
                # Track cache key for invalidation
                self.track_cache_key(key_prefix, cache_key)
                
                return result
            return wrapper
        return decorator
    
    def invalidate_by_prefix(self, prefix):
        """Invalidate all cache keys with given prefix"""
        pattern = f"cache_keys:{prefix}:*"
        keys = self.redis_client.keys(pattern)
        
        if keys:
            cache_keys = []
            for key in keys:
                cache_keys.extend(self.redis_client.smembers(key))
            
            # Delete cache entries
            if cache_keys:
                cache.delete_many(cache_keys)
            
            # Delete tracking keys
            self.redis_client.delete(*keys)
    
    def track_cache_key(self, prefix, cache_key):
        """Track cache keys for batch invalidation"""
        tracking_key = f"cache_keys:{prefix}"
        self.redis_client.sadd(tracking_key, cache_key)
        self.redis_client.expire(tracking_key, self.default_timeout + 300)

# Usage:
cache_manager = SmartCacheManager()

@cache_manager.cached_result('user_permissions', timeout=1800)
def get_user_permissions(user_id):
    # Expensive permission calculation
    return calculate_user_permissions(user_id)

# Invalidate when permissions change
def on_permission_change(user_id):
    cache_manager.invalidate_by_prefix('user_permissions')
```

### B. Conditional Caching Mixin
```python
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache.utils import make_template_fragment_key

class ConditionalCacheMixin:
    """Cache responses based on conditions"""
    cache_timeout = 300
    cache_conditions = []  # List of conditions to check
    
    def should_cache(self, request, *args, **kwargs):
        """Check if response should be cached"""
        if not self.cache_conditions:
            return True
        
        for condition in self.cache_conditions:
            if callable(condition):
                if not condition(request, *args, **kwargs):
                    return False
            elif isinstance(condition, str):
                # Check request attributes
                if not getattr(request, condition, True):
                    return False
        
        return True
    
    def get_cache_key(self, request, *args, **kwargs):
        """Generate cache key for request"""
        key_parts = [
            self.__class__.__name__,
            request.path,
            request.GET.urlencode(),
            str(request.user.id) if request.user.is_authenticated else 'anon'
        ]
        return make_template_fragment_key(':'.join(key_parts))
    
    def dispatch(self, request, *args, **kwargs):
        if self.should_cache(request, *args, **kwargs):
            cache_key = self.get_cache_key(request, *args, **kwargs)
            
            # Try to get cached response
            cached_response = cache.get(cache_key)
            if cached_response:
                return cached_response
            
            # Get fresh response
            response = super().dispatch(request, *args, **kwargs)
            
            # Cache successful responses
            if response.status_code == 200:
                cache.set(cache_key, response, self.cache_timeout)
            
            return response
        
        return super().dispatch(request, *args, **kwargs)

# Usage:
class ReportsViewSet(ConditionalCacheMixin, ModelViewSet):
    cache_timeout = 600
    cache_conditions = [
        lambda req, *args, **kwargs: req.method == 'GET',
        lambda req, *args, **kwargs: not req.GET.get('no_cache'),
        'user.is_active'  # Check request.user.is_active
    ]
```

## 3. Advanced Serializer Patterns

### A. Dynamic Field Serializer
```python
from rest_framework import serializers

class DynamicFieldsSerializer(serializers.ModelSerializer):
    """
    Serializer that allows dynamic field inclusion/exclusion
    """
    
    def __init__(self, *args, **kwargs):
        # Extract field control parameters
        fields = kwargs.pop('fields', None)
        exclude = kwargs.pop('exclude', None)
        expand = kwargs.pop('expand', None)
        
        super().__init__(*args, **kwargs)
        
        # Handle field inclusion/exclusion
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
        
        if exclude is not None:
            excluded = set(exclude)
            for field_name in excluded:
                self.fields.pop(field_name, None)
        
        # Handle field expansion
        if expand:
            self.expand_fields(expand)
    
    def expand_fields(self, expand_fields):
        """Dynamically add related fields"""
        for field_name in expand_fields:
            if hasattr(self.Meta.model, field_name):
                field = getattr(self.Meta.model, field_name)
                if hasattr(field, 'related'):
                    # Add related field serializer
                    related_model = field.related.related_model
                    self.fields[field_name] = self.get_related_serializer(related_model)()
    
    def get_related_serializer(self, model):
        """Get appropriate serializer for related model"""
        # Return basic serializer or lookup from registry
        class RelatedSerializer(serializers.ModelSerializer):
            class Meta:
                model = model
                fields = '__all__'
        return RelatedSerializer

# Usage:
class UserSerializer(DynamicFieldsSerializer):
    class Meta:
        model = User
        fields = '__all__'

# In views:
serializer = UserSerializer(
    users, 
    many=True,
    fields=['id', 'username', 'email'],  # Only these fields
    expand=['profile', 'roles']  # Include related data
)
```

### B. Conditional Field Serializer
```python
class ConditionalFieldsSerializer(serializers.ModelSerializer):
    """Show/hide fields based on user permissions or conditions"""
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        if self.request:
            self.filter_fields_by_permissions()
    
    def filter_fields_by_permissions(self):
        """Remove fields user doesn't have permission to see"""
        user = self.request.user
        
        # Define field permissions
        field_permissions = getattr(self.Meta, 'field_permissions', {})
        
        for field_name, required_permission in field_permissions.items():
            if not check_user_permission(user, required_permission):
                self.fields.pop(field_name, None)
    
    def get_field_value(self, field, obj):
        """Conditionally return field values"""
        # Check if field should be masked
        field_masks = getattr(self.Meta, 'field_masks', {})
        
        if field.field_name in field_masks:
            condition = field_masks[field.field_name]
            if callable(condition):
                if not condition(self.request, obj):
                    return "***HIDDEN***"
        
        return super().get_field_value(field, obj)

# Usage:
class UserDetailSerializer(ConditionalFieldsSerializer):
    class Meta:
        model = User
        fields = '__all__'
        field_permissions = {
            'ssn': 'view_sensitive_data',
            'salary': 'view_financial_data',
            'personal_notes': 'view_internal_notes'
        }
        field_masks = {
            'email': lambda req, obj: req.user != obj,  # Hide email from others
            'phone': lambda req, obj: req.user.has_perm('view_contact_info')
        }
```

## 4. Advanced Task Management

### A. Smart Task Retry System
```python
from celery import shared_task
from celery.exceptions import Retry
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SmartRetryTask:
    """Advanced task retry with exponential backoff and circuit breaker"""
    
    def __init__(self, max_retries=3, base_delay=60, max_delay=3600):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def __call__(self, func):
        @shared_task(bind=True, max_retries=self.max_retries)
        @wraps(func)
        def wrapper(task_self, *args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as exc:
                # Calculate retry delay with exponential backoff
                retry_count = task_self.request.retries
                delay = min(self.base_delay * (2 ** retry_count), self.max_delay)
                
                # Log the error
                logger.warning(f"Task {func.__name__} failed (attempt {retry_count + 1}): {exc}")
                
                # Check if we should retry
                if retry_count < self.max_retries:
                    logger.info(f"Retrying {func.__name__} in {delay} seconds")
                    raise task_self.retry(exc=exc, countdown=delay)
                else:
                    logger.error(f"Task {func.__name__} failed permanently after {retry_count + 1} attempts")
                    # Send failure notification
                    self.handle_permanent_failure(func.__name__, args, kwargs, exc)
                    raise exc
        
        return wrapper
    
    def handle_permanent_failure(self, task_name, args, kwargs, exception):
        """Handle permanent task failures"""
        # Send notification to admins
        from apps.notifications.tasks import send_admin_notification
        send_admin_notification.delay(
            subject=f"Task Failed Permanently: {task_name}",
            message=f"Task {task_name} failed after all retries. Exception: {exception}",
            metadata={'args': args, 'kwargs': kwargs}
        )

# Usage:
@SmartRetryTask(max_retries=5, base_delay=30)
def process_payment(payment_id):
    # Payment processing logic that might fail
    payment = Payment.objects.get(id=payment_id)
    result = external_payment_api.process(payment)
    return result
```

### B. Task Chain Builder
```python
from celery import chain, group, chord
from celery.canvas import Signature

class TaskChainBuilder:
    """Build complex task workflows"""
    
    def __init__(self):
        self.tasks = []
        self.groups = []
        self.callbacks = []
    
    def add_task(self, task, *args, **kwargs):
        """Add a task to the chain"""
        self.tasks.append(task.s(*args, **kwargs))
        return self
    
    def add_group(self, tasks):
        """Add parallel tasks"""
        self.groups.append(group(*tasks))
        return self
    
    def add_callback(self, callback_task, *args, **kwargs):
        """Add callback after all tasks complete"""
        self.callbacks.append(callback_task.s(*args, **kwargs))
        return self
    
    def build_chain(self):
        """Build the complete task chain"""
        if not self.tasks and not self.groups:
            return None
        
        all_tasks = self.tasks + self.groups
        
        if self.callbacks:
            # Use chord for callbacks after parallel execution
            return chord(all_tasks, self.callbacks[0])
        else:
            # Simple chain
            return chain(*all_tasks)
    
    def execute(self):
        """Execute the built chain"""
        task_chain = self.build_chain()
        if task_chain:
            return task_chain.apply_async()
        return None

# Usage:
def process_user_registration(user_id):
    """Complex user registration workflow"""
    builder = TaskChainBuilder()
    
    # Sequential tasks
    builder.add_task(validate_user_data, user_id)
    builder.add_task(create_user_profile, user_id)
    
    # Parallel tasks
    parallel_tasks = [
        send_welcome_email.s(user_id),
        setup_default_permissions.s(user_id),
        create_user_directory.s(user_id),
        initialize_user_settings.s(user_id)
    ]
    builder.add_group(parallel_tasks)
    
    # Callback after all complete
    builder.add_callback(finalize_registration, user_id)
    
    return builder.execute()
```

## 5. Advanced API Response Patterns

### A. Standardized API Response Wrapper
```python
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

class APIResponse:
    """Standardized API response format"""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK, meta=None):
        response_data = {
            'success': True,
            'message': message,
            'data': data,
            'timestamp': timezone.now().isoformat(),
            'status_code': status_code
        }
        
        if meta:
            response_data['meta'] = meta
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(message="An error occurred", errors=None, status_code=status.HTTP_400_BAD_REQUEST):
        response_data = {
            'success': False,
            'message': message,
            'errors': errors or [],
            'timestamp': timezone.now().isoformat(),
            'status_code': status_code
        }
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def paginated(data, page_info, message="Success"):
        return APIResponse.success(
            data=data,
            message=message,
            meta={
                'pagination': {
                    'page': page_info.get('page', 1),
                    'per_page': page_info.get('per_page', 20),
                    'total': page_info.get('total', 0),
                    'pages': page_info.get('pages', 0),
                    'has_next': page_info.get('has_next', False),
                    'has_prev': page_info.get('has_prev', False)
                }
            }
        )

# Usage in views:
class UserViewSet(ModelViewSet):
    def list(self, request):
        users = self.get_queryset()
        serializer = UserSerializer(users, many=True)
        
        return APIResponse.success(
            data=serializer.data,
            message="Users retrieved successfully"
        )
    
    def create(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return APIResponse.success(
                data=serializer.data,
                message="User created successfully",
                status_code=status.HTTP_201_CREATED
            )
        
        return APIResponse.error(
            message="Validation failed",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
```

### B. API Version Management
```python
from rest_framework.versioning import URLPathVersioning
from rest_framework.response import Response
from rest_framework import status

class SmartAPIVersioning(URLPathVersioning):
    """Enhanced API versioning with deprecation warnings"""
    
    version_deprecation_map = {
        'v1': {
            'deprecated': True,
            'sunset_date': '2024-12-31',
            'migration_guide': 'https://docs.example.com/api/v1-to-v2'
        }
    }
    
    def determine_version(self, request, *args, **kwargs):
        version = super().determine_version(request, *args, **kwargs)
        
        # Add deprecation headers if needed
        if version in self.version_deprecation_map:
            deprecation_info = self.version_deprecation_map[version]
            if deprecation_info.get('deprecated'):
                request.deprecated_version = True
                request.sunset_date = deprecation_info.get('sunset_date')
                request.migration_guide = deprecation_info.get('migration_guide')
        
        return version

class VersionAwareViewMixin:
    """Mixin to handle version-specific logic"""
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Add deprecation warnings
        if hasattr(request, 'deprecated_version'):
            response['X-API-Deprecated'] = 'true'
            if hasattr(request, 'sunset_date'):
                response['X-API-Sunset'] = request.sunset_date
            if hasattr(request, 'migration_guide'):
                response['X-API-Migration-Guide'] = request.migration_guide
        
        return response
    
    def get_serializer_class(self):
        """Return version-specific serializers"""
        version = getattr(self.request, 'version', 'v1')
        
        # Try to get version-specific serializer
        version_serializer = getattr(self, f'serializer_class_{version}', None)
        if version_serializer:
            return version_serializer
        
        return super().get_serializer_class()
```

## 6. Database Query Optimization Patterns

### A. Smart Query Builder
```python
from django.db.models import Prefetch, Q
from django.core.paginator import Paginator

class SmartQueryBuilder:
    """Build optimized database queries"""
    
    def __init__(self, model):
        self.model = model
        self.queryset = model.objects.all()
        self.select_related_fields = []
        self.prefetch_related_fields = []
        self.filters = Q()
        self.annotations = {}
    
    def add_select_related(self, *fields):
        """Add select_related optimization"""
        self.select_related_fields.extend(fields)
        return self
    
    def add_prefetch_related(self, field, queryset=None):
        """Add prefetch_related optimization"""
        if queryset:
            self.prefetch_related_fields.append(Prefetch(field, queryset=queryset))
        else:
            self.prefetch_related_fields.append(field)
        return self
    
    def add_filter(self, condition):
        """Add filter condition"""
        if isinstance(condition, Q):
            self.filters &= condition
        elif isinstance(condition, dict):
            self.filters &= Q(**condition)
        return self
    
    def add_annotation(self, **annotations):
        """Add annotations"""
        self.annotations.update(annotations)
        return self
    
    def build(self):
        """Build the optimized queryset"""
        queryset = self.queryset
        
        if self.select_related_fields:
            queryset = queryset.select_related(*self.select_related_fields)
        
        if self.prefetch_related_fields:
            queryset = queryset.prefetch_related(*self.prefetch_related_fields)
        
        if self.filters:
            queryset = queryset.filter(self.filters)
        
        if self.annotations:
            queryset = queryset.annotate(**self.annotations)
        
        return queryset

# Usage:
def get_user_with_roles_and_permissions(user_id):
    """Get user with all related data in optimal queries"""
    builder = SmartQueryBuilder(User)
    
    # Optimize related queries
    builder.add_select_related('profile', 'department')
    
    # Prefetch roles with their permissions
    role_prefetch = Prefetch(
        'roles',
        queryset=Role.objects.select_related().prefetch_related('permissions')
    )
    builder.add_prefetch_related('roles', role_prefetch.queryset)
    
    # Add filters
    builder.add_filter({'id': user_id, 'is_active': True})
    
    # Add useful annotations
    builder.add_annotation(
        total_permissions=Count('roles__permissions', distinct=True),
        last_login_days=ExpressionWrapper(
            Now() - F('last_login'),
            output_field=DurationField()
        )
    )
    
    return builder.build().first()
```

### B. Dynamic Filter System
```python
import django_filters
from django.db.models import Q

class DynamicFilterSet(django_filters.FilterSet):
    """Dynamic filter with search and advanced filtering"""
    
    search = django_filters.CharFilter(method='filter_search')
    date_range = django_filters.DateFromToRangeFilter()
    
    def filter_search(self, queryset, name, value):
        """Implement smart search across multiple fields"""
        if not value:
            return queryset
        
        # Get searchable fields from Meta
        search_fields = getattr(self.Meta, 'search_fields', [])
        
        if not search_fields:
            return queryset
        
        # Build search query
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": value})
        
        return queryset.filter(search_query)
    
    def filter_by_permissions(self, queryset, user):
        """Filter results based on user permissions"""
        if user.is_superuser:
            return queryset
        
        # Implement permission-based filtering
        # This would integrate with your permission system
        accessible_ids = get_user_accessible_resources(user, queryset.model)
        return queryset.filter(id__in=accessible_ids)
    
    @property
    def qs(self):
        """Override to add permission filtering"""
        queryset = super().qs
        
        # Add permission filtering if request available
        if hasattr(self, 'request') and self.request.user:
            queryset = self.filter_by_permissions(queryset, self.request.user)
        
        return queryset

# Usage:
class UserFilter(DynamicFilterSet):
    class Meta:
        model = User
        fields = {
            'is_active': ['exact'],
            'date_joined': ['gte', 'lte'],
            'user_type': ['exact', 'in']
        }
        search_fields = ['username', 'email', 'first_name', 'last_name']
```

## 7. Testing Utilities

### A. Test Data Factory
```python
import factory
from django.contrib.auth import get_user_model
from apps.permissions.models import Role, Permission

User = get_user_model()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    
    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for role in extracted:
                self.roles.add(role)

class PermissionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Permission
    
    name = factory.Faker('word')
    codename = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '_'))
    permission_type = 'feature'

class RoleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Role
    
    name = factory.Faker('job')
    description = factory.Faker('sentence')
    role_type = 'organizational'
    
    @factory.post_generation
    def permissions(self, create, extracted, **kwargs):
        if not create:
            return
        
        if extracted:
            for permission in extracted:
                self.permissions.add(permission)

# Test utilities
class TestDataMixin:
    """Mixin for test classes with common test data setup"""
    
    def setUp(self):
        super().setUp()
        self.setup_test_data()
    
    def setup_test_data(self):
        """Create common test data"""
        # Create permissions
        self.view_permission = PermissionFactory(
            name='View Data',
            codename='view_data'
        )
        self.edit_permission = PermissionFactory(
            name='Edit Data',
            codename='edit_data'
        )
        
        # Create roles
        self.viewer_role = RoleFactory(
            name='Viewer',
            permissions=[self.view_permission]
        )
        self.editor_role = RoleFactory(
            name='Editor',
            permissions=[self.view_permission, self.edit_permission]
        )
        
        # Create users
        self.viewer_user = UserFactory(roles=[self.viewer_role])
        self.editor_user = UserFactory(roles=[self.editor_role])
        self.admin_user = UserFactory(is_staff=True, is_superuser=True)
    
    def create_authenticated_client(self, user):
        """Create authenticated API client"""
        from rest_framework.test import APIClient
        from rest_framework.authtoken.models import Token
        
        client = APIClient()
        token, _ = Token.objects.get_or_create(user=user)
        client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        return client
```

## 8. Environment-Specific Configuration

### A. Smart Settings Management
```python
import os
from decouple import config

# Determine environment
ENVIRONMENT = config('DJANGO_ENV', default='development')

# Import environment-specific settings
if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'staging':
    from .staging import *
elif ENVIRONMENT == 'testing':
    from .testing import *
else:
    from .development import *

# Override with local settings if available
try:
    from .local import *
except ImportError:
    pass
```

```python
"""Base settings shared across all environments"""
import os
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Core settings
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_filters',
    # ... other third party apps
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.permissions',
    # ... your apps
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Reusable middleware configuration
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.SecurityHeadersMiddleware',
    'apps.core.middleware.RequestLoggingMiddleware',
]

# Database configuration helper
def get_database_config():
    """Get database configuration based on environment"""
    return {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME'),
            'USER': config('DB_USER'),
            'PASSWORD': config('DB_PASSWORD'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
            'OPTIONS': {
                'connect_timeout': 10,
            }
        }
    }

DATABASES = get_database_config()
```

These reusable patterns will significantly speed up your future Django REST Framework development by providing:

1. **Flexible Permission Systems** - Easy to extend and customize
2. **Smart Caching** - Performance optimization with minimal code
3. **Dynamic Serialization** - Adaptable API responses
4. **Robust Task Management** - Reliable background processing
5. **Standardized Responses** - Consistent API interface
6. **Optimized Queries** - Better database performance
7. **Comprehensive Testing** - Faster test development
8. **Environment Management** - Easy deployment configuration

Each pattern is designed to be modular and reusable across different projects while maintaining the high security and performance standards established in your current codebase.

