# Production Django REST Framework SAAS Application

A production-ready Django REST Framework application with government-level security, Firebase authentication, and comprehensive RBAC/ABAC authorization system.

## Features

### 🔐 Security Features
- **Multi-Factor Authentication (MFA)** with TOTP support
- **Firebase Authentication** integration
- **Role-Based Access Control (RBAC)**
- **Attribute-Based Access Control (ABAC)**
- **Account lockout** protection against brute force attacks
- **Comprehensive audit logging**
- **Session management** with device tracking
- **Password strength validation**
- **Rate limiting** and DDoS protection
- **Security headers** and CSP policies

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
- **Nginx** reverse proxy with security configurations
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

- **API Documentation**: http://localhost/api/docs/
- **Admin Interface**: http://localhost/admin/
- **API Endpoints**: http://localhost/api/v1/

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
```

### 2. SSL/TLS Configuration

Update `nginx/nginx.conf` to enable HTTPS:
```nginx
server {
    listen 443 ssl http2;
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    # ... additional SSL configuration
}
```

### 3. Database Security

```sql
-- Create dedicated database user
CREATE USER saas_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE saas_app TO saas_app;
GRANT USAGE ON SCHEMA public TO saas_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO saas_app;
```

### 4. Monitoring Setup

Configure Sentry for error tracking:
```python
SENTRY_DSN = 'your-sentry-dsn'
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
│          Django Security            │
├─────────────────────────────────────┤
│        Permission System            │
├─────────────────────────────────────┤
│         Authentication              │
├─────────────────────────────────────┤
│            Nginx Proxy              │
├─────────────────────────────────────┤
│         Network Security            │
└─────────────────────────────────────┘
```

## Troubleshooting

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
