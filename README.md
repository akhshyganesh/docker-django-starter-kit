# 🚀 Django REST Framework SAAS Starter Kit

> **A complete, production-ready Django REST Framework application with enterprise-grade security and modern architecture.**

This starter kit provides everything you need to build a scalable SAAS application with government-level security, comprehensive user management, and advanced permission systems - all ready to deploy in minutes!

---

## ✨ What Makes This Special?

- **🔒 Enterprise Security**: Government-grade security with MFA, RBAC/ABAC, and audit logging
- **⚡ Production Ready**: Docker-containerized with PostgreSQL, Redis, and Celery
- **🎯 No Reverse Proxy Needed**: Built-in rate limiting and security features
- **📱 Modern Auth**: Firebase integration + traditional authentication
- **🔧 Developer Friendly**: Comprehensive API docs, testing suite, and clear structure
- **📊 Monitoring Built-in**: Health checks, logging, and error tracking

---

## 🎯 Perfect For

- **SAAS Applications** requiring user management and subscriptions
- **Enterprise Systems** needing advanced security and compliance
- **API-First Applications** with mobile/web frontends
- **Multi-tenant Platforms** with role-based access control
- **Government/Financial Apps** requiring audit trails and security

---

## 🏗️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend** | Django 4.2 LTS + DRF | Stable, secure web framework |
| **Database** | PostgreSQL | Production-grade relational database |
| **Cache** | Redis | Session storage, caching, rate limiting |
| **Task Queue** | Celery | Background jobs and async processing |
| **Authentication** | Firebase + JWT | Modern auth with MFA support |
| **Security** | Django Axes + Custom | Brute force protection and monitoring |
| **Deployment** | Docker + Docker Compose | Containerized deployment |

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- **Docker & Docker Compose** (Get it [here](https://docs.docker.com/get-docker/))
- **Git** for cloning the repository

### Step 1: Clone & Setup
```bash
# Clone the repository
git clone <repository-url>
cd docker-django-starter-kit

# Copy environment template
cp .env.example .env
```

### Step 2: Configure Environment
Open `.env` file and update these essential settings:

```bash
# � Security (Generate a secure key)
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random

# 🌐 Domain Settings
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://your-domain.com

# 💾 Database (Use strong passwords)
POSTGRES_DB=saas_app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-database-password

# 🔥 Firebase (Optional - for social login)
FIREBASE_PROJECT_ID=your-firebase-project-id
# Add other Firebase settings if needed
```

### Step 3: Launch Application
```bash
# Build and start all services
docker-compose up -d --build

# Wait for services to start (check with)
docker-compose ps

# Initialize the database and create default roles/permissions
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py create_default_permissions

# Create your admin account
docker-compose exec web python manage.py createsuperuser
```

### Step 4: Verify Installation
- **🌐 API Documentation**: http://localhost:8000/api/docs/
- **⚙️ Admin Panel**: http://localhost:8000/admin/
- **🔍 Health Check**: http://localhost:8000/health/
- **📊 API Base**: http://localhost:8000/api/v1/

**🎉 That's it! Your application is running!**

---

## 📚 Understanding the Application

### 🔐 Security Features

#### **Multi-Layer Security Architecture**
```
┌────────────────────────────────┐
│     🌐 Request Layer           │
│  Rate Limiting + IP Filtering  │
├────────────────────────────────┤
│     🔐 Authentication Layer    │
│  Firebase + JWT + MFA          │
├────────────────────────────────┤
│     🛡️ Authorization Layer     │
│  RBAC + ABAC + Permissions     │
├────────────────────────────────┤
│     📊 Audit Layer             │
│  Logging + Monitoring          │
└────────────────────────────────┘
```

#### **Key Security Features**
- **🔒 Strong Authentication**: 12+ character passwords, MFA support, account lockout
- **🛡️ Authorization Control**: Role-based + Attribute-based access control
- **🚫 Attack Prevention**: Rate limiting, brute force protection, suspicious activity detection
- **📋 Compliance Ready**: Comprehensive audit logs, data encryption, GDPR compliance
- **🔍 Monitoring**: Real-time security monitoring and alerting

### 👥 User Management System

#### **User Types & Roles**
- **🔧 System Roles**: Super Admin, Admin, Manager
- **👤 User Roles**: Employee, Client, Guest
- **⚙️ Custom Roles**: Create your own with specific permissions

#### **User Lifecycle**
```
Registration → Email Verification → Profile Setup → Role Assignment → Active User
     ↓              ↓                   ↓              ↓              ↓
  [Pending]    [Unverified]        [Inactive]     [Assigned]     [Active]
```

### 🔑 Permission System

#### **How Permissions Work**
1. **👤 Users** are assigned **🎭 Roles**
2. **🎭 Roles** contain multiple **🔑 Permissions**
3. **🔑 Permissions** can be **⏰ Time-limited** or **📍 Resource-specific**
4. **🤖 System** checks permissions on every API request

#### **Permission Types**
- **📂 Resource**: Access to specific data (users, projects, reports)
- **⚡ Action**: Specific operations (create, read, update, delete, export)
- **🎯 Feature**: Application features (dashboard, billing, analytics)
- **🔧 API**: API endpoint access
- **👑 Admin**: Administrative functions

---

## 📖 Complete API Guide

### 🔐 Authentication APIs

#### **User Registration**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

#### **User Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

#### **Firebase Social Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/firebase-login/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <firebase-id-token>" \
  -d '{
    "firebase_token": "<firebase-id-token>"
  }'
```

### 👤 User Management APIs

#### **Get Current User Profile**
```bash
curl -X GET http://localhost:8000/api/v1/users/me/ \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### **List All Users** (Admin only)
```bash
curl -X GET http://localhost:8000/api/v1/users/ \
  -H "Authorization: Bearer <admin-jwt-token>"
```

#### **Assign Role to User**
```bash
curl -X POST http://localhost:8000/api/v1/users/{user_id}/assign-role/ \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "role-uuid-here"
  }'
```

### 🔑 Permission Management APIs

#### **List Available Roles**
```bash
curl -X GET http://localhost:8000/api/v1/permissions/roles/ \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### **Create New Role**
```bash
curl -X POST http://localhost:8000/api/v1/permissions/roles/ \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Project Manager",
    "is_active": true
  }'
```

#### **Assign Permission to Role**
```bash
curl -X POST http://localhost:8000/api/v1/permissions/roles/{role_id}/assign-permission/ \
  -H "Authorization: Bearer <admin-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "permission_id": "permission-uuid-here"
  }'
```

### 🔒 Multi-Factor Authentication

#### **Setup MFA**
```bash
curl -X POST http://localhost:8000/api/v1/auth/mfa/setup/ \
  -H "Authorization: Bearer <your-jwt-token>"
```

#### **Verify MFA Token**
```bash
curl -X POST http://localhost:8000/api/v1/auth/mfa/verify/ \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "123456"
  }'
```

### 📊 System APIs

#### **Health Check**
```bash
curl -X GET http://localhost:8000/health/
```

#### **Security Test**
```bash
curl -X GET http://localhost:8000/security-test/
```

---

## ⚙️ Configuration Guide

### 🔧 Environment Variables

Create and customize your `.env` file:

```bash
# 🔐 Security Configuration
SECRET_KEY=django-insecure-your-super-secret-key-here
DEBUG=False
DJANGO_ENV=production

# 🌐 Domain & CORS Settings
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
CSRF_TRUSTED_ORIGINS=http://localhost:8000,https://yourdomain.com
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourfrontend.com

# 💾 Database Configuration
POSTGRES_DB=saas_app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# 🔴 Redis Configuration
REDIS_URL=redis://redis:6379/0

# 🔥 Firebase Authentication (Optional)
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com

# 📧 Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# 🚨 Monitoring & Error Tracking
SENTRY_DSN=your-sentry-dsn-here

# 🔒 Security Settings
SESSION_COOKIE_SECURE=False  # Set True for HTTPS
CSRF_COOKIE_SECURE=False     # Set True for HTTPS
SECURE_SSL_REDIRECT=False    # Set True for HTTPS

# 🚦 Rate Limiting
RATELIMIT_ENABLE=True

# 🏠 Admin Security
ADMIN_ALLOWED_IPS=127.0.0.1,192.168.1.0/24  # Comma-separated IPs/subnets
```

### 🔒 Security Settings Explained

| Setting | Purpose | Production Value |
|---------|---------|------------------|
| `SECRET_KEY` | Django encryption key | 50+ random characters |
| `DEBUG` | Development mode | `False` |
| `ALLOWED_HOSTS` | Allowed domains | Your actual domains |
| `CSRF_TRUSTED_ORIGINS` | CSRF protection | Your HTTPS domains |
| `SESSION_COOKIE_SECURE` | HTTPS-only cookies | `True` for HTTPS |
| `ADMIN_ALLOWED_IPS` | Admin IP whitelist | Your office IPs |

---

## 🚢 Production Deployment

### 🌐 Deploy to Production Server

#### **1. Prepare Server**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin -y
```

#### **2. Clone and Configure**
```bash
# Clone repository
git clone <your-repo-url>
cd docker-django-starter-kit

# Set production environment
cp .env.example .env
# Edit .env with production values
nano .env
```

#### **3. Deploy**
```bash
# Build and start
docker compose up -d --build

# Initialize database
docker compose exec web python manage.py migrate
docker compose exec web python manage.py create_default_permissions
docker compose exec web python manage.py createsuperuser

# Collect static files
docker compose exec web python manage.py collectstatic --noinput
```

### 🔒 Production Security Checklist

- [ ] **Strong `SECRET_KEY`** (50+ random characters)
- [ ] **`DEBUG=False`** in production
- [ ] **HTTPS enabled** with valid SSL certificate
- [ ] **Secure cookies** (`SESSION_COOKIE_SECURE=True`)
- [ ] **Admin IP whitelist** configured
- [ ] **Strong database passwords**
- [ ] **Firewall configured** (ports 80, 443 only)
- [ ] **Regular backups** scheduled
- [ ] **Monitoring** set up (Sentry, logs)
- [ ] **Domain verification** in `ALLOWED_HOSTS`

### 📊 Monitoring & Maintenance

#### **View Logs**
```bash
# Application logs
docker compose logs web -f

# Database logs
docker compose logs db -f

# Background tasks
docker compose logs celery -f

# All services
docker compose logs -f
```

#### **Database Backup**
```bash
# Create backup
docker compose exec db pg_dump -U postgres saas_app > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker compose exec -T db psql -U postgres saas_app < backup_file.sql
```

#### **Health Monitoring**
```bash
# Check all services
docker compose ps

# Resource usage
docker stats

# Application health
curl http://localhost:8000/health/
```

---

## 🧪 Development Guide

### 🔧 Local Development Setup

#### **Method 1: Using Docker (Recommended)**
```bash
# Clone repository
git clone <repository-url>
cd docker-django-starter-kit

# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# Install development dependencies
docker-compose exec web pip install -r requirements-dev.txt
```

#### **Method 2: Local Python Environment**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Setup database (PostgreSQL required)
python manage.py migrate
python manage.py create_default_permissions
python manage.py createsuperuser
```

### 🧪 Testing

#### **Run All Tests**
```bash
# Using Docker
docker-compose exec web python manage.py test

# Local environment
python manage.py test
```

#### **Run Specific Tests**
```bash
# Test specific app
docker-compose exec web python manage.py test apps.users

# Test specific file
docker-compose exec web python manage.py test apps.users.tests.test_models

# Test with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
docker-compose exec web coverage html  # HTML report
```

#### **Test Categories**
- **Unit Tests**: Individual component testing
- **Integration Tests**: API endpoint testing
- **Security Tests**: Authentication and authorization
- **Performance Tests**: Load and stress testing

### 🔄 Database Operations

#### **Migrations**
```bash
# Create new migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Show migration status
docker-compose exec web python manage.py showmigrations

# Create empty migration
docker-compose exec web python manage.py makemigrations --empty your_app_name
```

#### **Database Management**
```bash
# Access database shell
docker-compose exec db psql -U postgres saas_app

# Django database shell
docker-compose exec web python manage.py dbshell

# Reset database (⚠️ Destructive)
docker-compose exec web python manage.py flush
```

### 📝 Code Quality

#### **Linting & Formatting**
```bash
# Format code with Black
docker-compose exec web black .

# Check with flake8
docker-compose exec web flake8 .

# Sort imports with isort
docker-compose exec web isort .

# Type checking with mypy
docker-compose exec web mypy .
```

### 🔄 Background Tasks

#### **Celery Development**
```bash
# Start Celery worker
docker-compose exec celery celery -A core worker -l info

# Start Celery beat (scheduler)
docker-compose exec celery-beat celery -A core beat -l info

# Monitor tasks
docker-compose exec celery celery -A core flower
# Visit: http://localhost:5555
```

---

## 🛠️ Customization Guide

### 🎨 Adding New Features

#### **1. Create New Django App**
```bash
# Create app
docker-compose exec web python manage.py startapp your_app_name

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS = [
    # ...existing apps...
    'apps.your_app_name',
]
```

#### **2. Add API Endpoints**
```python
# apps/your_app_name/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    permission_classes = [IsAuthenticated]
```

#### **3. Configure URLs**
```python
# apps/your_app_name/urls.py
from rest_framework.routers import DefaultRouter
from .views import YourModelViewSet

router = DefaultRouter()
router.register(r'your-models', YourModelViewSet)
urlpatterns = router.urls

# core/urls.py - Add to main URL configuration
urlpatterns = [
    # ...existing patterns...
    path('api/v1/your-app/', include('apps.your_app_name.urls')),
]
```

### 🔐 Custom Permissions

#### **Create Custom Permission**
```python
# apps/permissions/custom_permissions.py
from rest_framework.permissions import BasePermission
from .utils import check_user_permission

class CanAccessBillingPermission(BasePermission):
    """
    Custom permission to check if user can access billing
    """
    def has_permission(self, request, view):
        return check_user_permission(
            request.user, 
            'access_billing', 
            request=request
        )

# Use in views
class BillingViewSet(viewsets.ModelViewSet):
    permission_classes = [CanAccessBillingPermission]
```

#### **Add Permission to Database**
```python
# Create via Django shell
from apps.permissions.models import Permission

Permission.objects.create(
    name="Can Access Billing",
    description="Access to billing and payment features"
)
```

### 🎯 Custom User Fields

#### **Extend User Model**
```python
# apps/users/models.py
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Add your custom fields
    company_name = models.CharField(max_length=200, blank=True)
    subscription_tier = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('pro', 'Pro'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    # ...existing fields...
```

### 📊 Custom Analytics

#### **Add Analytics Tracking**
```python
# apps/analytics/models.py
class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict)

# apps/analytics/middleware.py
class AnalyticsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track user activity
        response = self.get_response(request)
        # Log activity
        return response
```

---

## 🔍 Troubleshooting

### 🚨 Common Issues & Solutions

#### **🔌 Database Connection Issues**
```bash
# Problem: Can't connect to database
# Solution: Check database status
docker-compose ps db
docker-compose logs db

# Reset database connection
docker-compose restart db
docker-compose exec web python manage.py migrate
```

#### **🔑 Permission Denied Errors**
```bash
# Problem: User can't access certain endpoints
# Solution: Check user permissions
docker-compose exec web python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.user_permissions.all()
>>> user.groups.all()
```

#### **🔒 MFA Issues**
```bash
# Problem: MFA setup failing
# Solution: Reset MFA for user
docker-compose exec web python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='user@example.com')
>>> user.mfa_enabled = False
>>> user.mfa_secret = ''
>>> user.save()
```

#### **🐌 Slow API Responses**
```bash
# Problem: API endpoints are slow
# Solutions:
# 1. Check Redis connection
docker-compose logs redis

# 2. Monitor database queries
docker-compose exec web python manage.py shell
>>> from django.db import connection
>>> print(len(connection.queries))

# 3. Check Celery workers
docker-compose logs celery
```

#### **📝 Migration Issues**
```bash
# Problem: Migration conflicts
# Solution: Reset migrations (⚠️ Development only)
docker-compose exec web python manage.py migrate your_app_name zero
docker-compose exec web python manage.py makemigrations your_app_name
docker-compose exec web python manage.py migrate

# For production: Create merge migration
docker-compose exec web python manage.py makemigrations --merge
```

### 📞 Getting Help

#### **Debug Mode**
```python
# For development debugging
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

#### **Performance Profiling**
```bash
# Install django-debug-toolbar for development
pip install django-debug-toolbar

# Add to development settings
INSTALLED_APPS = [
    # ...
    'debug_toolbar',
]

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # ...existing middleware...
]
```

---

## 📚 Additional Resources

### 📖 Documentation Links
- **[Django Documentation](https://docs.djangoproject.com/)**
- **[Django REST Framework](https://www.django-rest-framework.org/)**
- **[Docker Documentation](https://docs.docker.com/)**
- **[PostgreSQL Documentation](https://www.postgresql.org/docs/)**
- **[Redis Documentation](https://redis.io/documentation)**
- **[Celery Documentation](https://docs.celeryproject.org/)**

### 🎓 Learning Resources
- **[Django for Beginners](https://djangoforbeginners.com/)**
- **[DRF Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/)**
- **[Docker Tutorial](https://docker-curriculum.com/)**
- **[API Design Best Practices](https://restfulapi.net/)**

### 🏗️ Architecture Patterns
- **[Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)**
- **[Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)**
- **[Microservices Patterns](https://microservices.io/patterns/)**

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 🔄 Contribution Workflow

1. **🍴 Fork the repository**
2. **🌿 Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **💻 Make your changes**
4. **🧪 Add/update tests**
5. **✅ Ensure all tests pass**
   ```bash
   docker-compose exec web python manage.py test
   ```
6. **📝 Update documentation if needed**
7. **🚀 Submit a pull request**

### 📋 Contribution Guidelines

- **Code Style**: Follow PEP 8 and use Black for formatting
- **Tests**: Add tests for new features
- **Documentation**: Update README and docstrings
- **Security**: Security-related changes need extra review
- **Performance**: Profile performance-critical changes

### 🐛 Bug Reports

When reporting bugs, please include:
- **Environment details** (OS, Python version, Docker version)
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Log files** or error messages
- **Screenshots** if applicable

### 💡 Feature Requests

For new features, please:
- **Describe the use case** and problem it solves
- **Provide examples** of how it would be used
- **Consider the impact** on existing functionality
- **Discuss the implementation** approach

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### 📋 License Summary
- ✅ **Commercial Use**: Use for commercial projects
- ✅ **Modification**: Modify the code
- ✅ **Distribution**: Distribute the code
- ✅ **Private Use**: Use privately
- ❗ **Liability**: No warranty provided
- ❗ **Attribution**: Credit the original authors

---

## 🆘 Support & Community

### 💬 Getting Support

- **📚 Documentation**: Check this README and inline documentation
- **🐛 Issues**: Create a GitHub issue for bugs
- **💡 Discussions**: Use GitHub Discussions for questions
- **📧 Email**: Contact the maintainers for security issues

### 🌟 Show Your Support

If this project helped you, please:
- ⭐ **Star the repository**
- 🍴 **Fork it** for your own projects
- 📢 **Share it** with others
- 🤝 **Contribute** back to the community

---

## 🏆 Acknowledgments

Special thanks to:
- **Django Community** for the amazing framework
- **DRF Team** for the REST framework
- **Security Researchers** for best practices
- **Open Source Contributors** for inspiration
- **Community Members** for feedback and testing

---

<div align="center">

**🚀 Ready to build amazing SAAS applications?**

[Get Started](#-quick-start-5-minutes) | [View Docs](#-complete-api-guide) | [Join Community](#-support--community)

Made with ❤️ by developers, for developers

</div>
