# Production Django REST Framework SAAS Application

A production-ready Django REST Framework application with enterprise-level security, Firebase authentication, and comprehensive RBAC/ABAC authorization system optimized for direct deployment without reverse proxy.

## Features

### 🔐 Security Features
- **Multi-Factor Authentication (MFA)** with TOTP support
- **Firebase Authentication** integration
- **Role-Based Access Control (RBAC)**
- **Attribute-Based Access Control (ABAC)**
- **Enhanced brute force protection** with Django Axes
- **Comprehensive audit logging**
- **Session management** with device tracking
- **Advanced password complexity validation**
- **Built-in rate limiting** without reverse proxy dependency
- **Security headers** and strict CSP policies
- **IP-based access control** for admin interface
- **Suspicious activity detection and logging**

### 👥 User Management
- Custom user model with extended fields
- User profiles with personal and professional information
- User type classification (Admin, Manager, Employee, Client, Guest)
- Account status management (Active, Inactive, Suspended, Locked, Pending)
- Timezone and localization support
- Privacy and notification preferences

### 🔑 Permission System
- **Dynamic permission system** supporting both RBAC and ABAC
- **Hierarchical roles** with inheritance
- **Time-based permissions** with expiration
- **Resource-level permissions** for fine-grained access control
- **Policy rules engine** for complex authorization logic
- **Permission caching** for performance optimization

### 🏗️ Architecture
- **Docker containerization** with production-ready configuration
- **PostgreSQL** database with optimized indexes
- **Redis** caching and session storage
- **Celery** for background task processing
- **Direct Django deployment** with built-in security
- **Comprehensive logging** with structured format
- **Health checks** and monitoring endpoints

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
git clone <repository-url>
cd docker-django-starter-kit
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file with your settings:

```bash
# Essential settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,localhost
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Database
POSTGRES_DB=saas_app
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password

# Firebase (optional)
FIREBASE_PROJECT_ID=your-firebase-project
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
```

### 3. Build and Run

```bash
# Build and start services
docker-compose up -d --build

# Create default permissions and roles
docker-compose exec web python manage.py create_default_permissions

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### 4. Access the Application

- **API Documentation**: http://localhost:8000/api/docs/
- **Admin Interface**: http://localhost:8000/admin/
- **API Endpoints**: http://localhost:8000/api/v1/

## API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "password_confirm": "SecurePassword123!",
    "first_name": "John",
    "last_name": "Doe"
}
```

#### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "SecurePassword123!"
}
```

#### Firebase Login
```http
POST /api/v1/auth/firebase-login/
Content-Type: application/json
Authorization: Bearer <firebase-id-token>

{
    "firebase_token": "<firebase-id-token>"
}
```

### User Management Endpoints

#### Get Current User
```http
GET /api/v1/users/me/
Authorization: Bearer <token>
```

#### List Users (Admin)
```http
GET /api/v1/users/
Authorization: Bearer <token>
```

#### Assign Role to User
```http
POST /api/v1/users/{user_id}/assign-role/
Authorization: Bearer <token>
Content-Type: application/json

{
    "role_id": "role-uuid"
}
```

### Permission Management

#### List Roles
```http
GET /api/v1/permissions/roles/
Authorization: Bearer <token>
```

#### Assign Permission to Role
```http
POST /api/v1/permissions/roles/{role_id}/assign-permission/
Authorization: Bearer <token>
Content-Type: application/json

{
    "permission_id": "permission-uuid"
}
```

### Multi-Factor Authentication

#### Setup MFA
```http
POST /api/v1/auth/mfa/setup/
Authorization: Bearer <token>
```

#### Verify MFA
```http
POST /api/v1/auth/mfa/verify/
Authorization: Bearer <token>
Content-Type: application/json

{
    "token": "123456"
}
```

## Security Configuration

### Government-Level Security Features

1. **Authentication Security**
   - Minimum 12-character passwords with complexity requirements
   - Account lockout after 5 failed attempts
   - Session timeout and concurrent session limits
   - MFA enforcement for privileged accounts

2. **Authorization Security**
   - Principle of least privilege
   - Role-based and attribute-based access control
   - Time-based access controls
   - Resource-level permissions

3. **Data Protection**
   - Encryption at rest and in transit
   - Audit logging for all sensitive operations
   - Data anonymization and pseudonymization
   - Secure data deletion

4. **Network Security**
   - Rate limiting and DDoS protection
   - Security headers (HSTS, CSP, etc.)
   - CORS configuration
   - IP whitelist/blacklist support

5. **Monitoring and Compliance**
   - Comprehensive audit trails
   - Security incident detection
   - Compliance reporting
   - Automated security scanning

## Production Deployment

### 1. Security Hardening

```bash
# Generate secure secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Set production environment
export DJANGO_ENV=production
export DEBUG=False

# Configure allowed hosts for your domain
export ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
export CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 2. Security Configuration

The application includes built-in security features:

- **Rate Limiting**: Configurable per endpoint
- **IP Whitelisting**: For admin access
- **Security Headers**: Automatically applied
- **Brute Force Protection**: Enhanced with Django Axes
- **Password Policy**: Complex validation rules
- **Session Security**: Secure cookie settings

### 3. Database Security

```sql
-- Create dedicated database user
CREATE USER saas_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE saas_app TO saas_app;
GRANT USAGE ON SCHEMA public TO saas_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO saas_app;
```

### 4. Environment Variables

Essential production settings:

```env
DJANGO_ENV=production
DEBUG=False
SECRET_KEY=your-super-secure-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Security Settings
SESSION_COOKIE_SECURE=False  # Set to True if using HTTPS
CSRF_COOKIE_SECURE=False     # Set to True if using HTTPS
SECURE_SSL_REDIRECT=False    # Set to True if using HTTPS
SECURE_HSTS_SECONDS=0        # Set to 31536000 if using HTTPS

# Rate Limiting
RATELIMIT_ENABLE=True

# Admin IP Whitelist (comma-separated)
ADMIN_ALLOWED_IPS=127.0.0.1,your-office-ip

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

### 5. Gunicorn Configuration

The application includes an optimized Gunicorn configuration file (`gunicorn.conf.py`) with production-ready security and performance settings:

#### Key Security Features:
- **Request size limits** to prevent abuse attacks
- **Worker process isolation** with automatic restarts
- **Comprehensive logging** for security monitoring
- **Resource optimization** with shared memory usage
- **Graceful shutdowns** to prevent data loss

#### Configuration Highlights:
```python
# Automatically scales workers based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1

# Security limits
limit_request_line = 4094      # Max HTTP request line size
limit_request_fields = 100     # Max number of header fields
limit_request_field_size = 8190 # Max header field size

# Performance optimizations
max_requests = 1000            # Restart workers after 1000 requests
max_requests_jitter = 50       # Add randomness to prevent thundering herd
worker_tmp_dir = "/dev/shm"    # Use shared memory for better performance
```

#### Production Deployment Command:
```bash
# The entrypoint script automatically uses the optimized configuration
# when DJANGO_ENV=production
export DJANGO_ENV=production
docker-compose up -d
```

#### Monitoring Gunicorn:
```bash
# Check worker status
docker-compose exec web ps aux | grep gunicorn

# Monitor access logs
docker-compose exec web tail -f /app/logs/gunicorn_access.log

# Monitor error logs
docker-compose exec web tail -f /app/logs/gunicorn_error.log
```

## Development

### Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test apps.users

# Run with coverage
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```

### Database Migrations

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

### Background Tasks

```bash
# Start Celery worker
docker-compose exec celery celery -A core worker -l info

# Start Celery beat scheduler
docker-compose exec celery-beat celery -A core beat -l info
```

## Architecture Details

### Permission System Architecture

The application implements a hybrid RBAC/ABAC system:

1. **RBAC (Role-Based Access Control)**
   - Users are assigned roles
   - Roles have permissions
   - Hierarchical role inheritance

2. **ABAC (Attribute-Based Access Control)**
   - Context-aware permissions
   - Time-based access controls
   - Environmental attributes (IP, location, time)
   - Resource attributes

3. **Permission Evaluation Flow**
   ```
   Request → Authentication → Permission Check → ABAC Rules → Access Decision
   ```

### Security Layers

```
┌─────────────────────────────────────┐
│            Application              │
├─────────────────────────────────────┤
│      Security Middleware           │
├─────────────────────────────────────┤
│        Permission System            │
├─────────────────────────────────────┤
│         Authentication              │
├─────────────────────────────────────┤
│         Rate Limiting               │
├─────────────────────────────────────┤
│         Network Security            │
└─────────────────────────────────────┘
```

## Built-in Security Features

### 1. **Authentication Security**
   - Minimum 12-character passwords with complexity requirements
   - Account lockout after 5 failed attempts with 1-hour cooldown
   - Session timeout and concurrent session limits
   - MFA enforcement for privileged accounts
   - Password history tracking (prevents reuse of last 5 passwords)

### 2. **Authorization Security**
   - Principle of least privilege
   - Role-based and attribute-based access control
   - Time-based access controls
   - Resource-level permissions
   - IP-based access restrictions for admin interface

### 3. **Network Security**
   - Built-in rate limiting (per IP, per endpoint)
   - Security headers (X-Frame-Options, CSP, XSS Protection)
   - CORS configuration
   - IP whitelist for admin access
   - Suspicious activity detection

### 4. **Data Protection**
   - Encrypted sessions and cookies
   - Audit logging for all sensitive operations
   - Secure password hashing (Django's PBKDF2)
   - Database connection security
   - Input validation and sanitization

### 5. **Monitoring and Compliance**
   - Comprehensive audit trails
   - Security incident detection and logging
   - Real-time attack pattern recognition
   - Failed authentication tracking
   - Admin access monitoring

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check database status
   docker-compose exec db pg_isready
   
   # View database logs
   docker-compose logs db
   ```

2. **Permission Denied Errors**
   ```bash
   # Check user permissions
   docker-compose exec web python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> user = User.objects.get(email='user@example.com')
   >>> user.get_permissions()
   ```

3. **MFA Setup Issues**
   ```bash
   # Reset MFA for user
   docker-compose exec web python manage.py shell
   >>> user.mfa_enabled = False
   >>> user.mfa_secret = ''
   >>> user.save()
   ```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please create an issue in the repository or contact the development team.

---

**Note**: This is a production-ready template. Always review and customize security settings for your specific use case and compliance requirements.
