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

### 🚀 Quick Production Setup

1. **Clone and Configure**
```bash
git clone <your-repository>
cd docker-django-starter-kit
cp .env.example .env
```

2. **Security Setup**
```bash
chmod +x security-setup.sh
./security-setup.sh all
```

3. **Update Environment Configuration**
Edit `.env` file with your production values:
- Set `DEBUG=False`
- Configure your domain in `ALLOWED_HOSTS`
- Set strong database passwords
- Configure SSL certificates
- Set up monitoring credentials

4. **Deploy to Production**
```bash
chmod +x deploy.sh
./deploy.sh deploy
```

### 🔒 Security Hardening

#### 1. Generate Secure Credentials
```bash
# Generate secure secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Generate secure database password
openssl rand -base64 32
```

#### 2. SSL/TLS Configuration

**For Production:**
- Obtain SSL certificate from a trusted CA (Let's Encrypt, etc.)
- Place certificates in `nginx/ssl/` directory
- Update domain name in `nginx/nginx.production.conf`

**For Testing:**
```bash
# Generate self-signed certificate (development only)
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### 3. Database Security
```sql
-- Create dedicated database user with limited privileges
CREATE USER saas_app WITH PASSWORD 'secure_password';
CREATE DATABASE saas_production OWNER saas_app;
GRANT CONNECT ON DATABASE saas_production TO saas_app;
GRANT USAGE ON SCHEMA public TO saas_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO saas_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO saas_app;
```

#### 4. Firewall Configuration
```bash
# Ubuntu/Debian firewall setup
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 📊 Monitoring Setup

#### Health Checks
- **Application Health**: `https://your-domain.com/api/v1/health/`
- **Readiness Check**: `https://your-domain.com/api/v1/ready/`
- **Liveness Check**: `https://your-domain.com/api/v1/live/`

#### Monitoring Tools
- **Flower (Celery)**: `https://your-domain.com/flower/`
- **Admin Panel**: `https://your-domain.com/admin/`
- **API Documentation**: `https://your-domain.com/api/docs/`

#### Log Monitoring
```bash
# View application logs
./deploy.sh logs web

# View all service logs
./deploy.sh logs

# Monitor system status
./monitor.sh
```

### 🔄 Backup and Recovery

#### Automated Backups
```bash
# Create backup
./deploy.sh backup

# Schedule daily backups (crontab)
0 2 * * * /path/to/project/backup.sh
```

#### Manual Database Backup
```bash
# Create backup
docker-compose -f docker-compose.production.yml exec db pg_dump -U saas_user saas_production > backup.sql

# Restore backup
docker-compose -f docker-compose.production.yml exec -T db psql -U saas_user saas_production < backup.sql
```

### ⚖️ Scaling

#### Horizontal Scaling
```bash
# Scale web servers
docker-compose -f docker-compose.production.yml up -d --scale web=3

# Scale Celery workers
docker-compose -f docker-compose.production.yml up -d --scale celery=2
```

#### Load Balancer Configuration
Update `nginx/nginx.production.conf` upstream configuration:
```nginx
upstream django {
    server web:8000;
    server web_2:8000;
    server web_3:8000;
}
```

### 🛠️ Maintenance

#### Service Management
```bash
# Check service status
./deploy.sh status

# View logs
./deploy.sh logs [service_name]

# Restart services
docker-compose -f docker-compose.production.yml restart

# Update application
git pull
docker-compose -f docker-compose.production.yml build --no-cache
docker-compose -f docker-compose.production.yml up -d
```

#### Database Migrations
```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec web python manage.py migrate

# Create superuser
docker-compose -f docker-compose.production.yml exec web python manage.py createsuperuser

# Collect static files
docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput
```

### 🚨 Troubleshooting

#### Common Issues

1. **SSL Certificate Issues**
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Test SSL configuration
curl -I https://your-domain.com
```

2. **Database Connection Issues**
```bash
# Check database connectivity
docker-compose -f docker-compose.production.yml exec web python manage.py dbshell

# Check database logs
docker-compose -f docker-compose.production.yml logs db
```

3. **Service Health Issues**
```bash
# Check service health
curl https://your-domain.com/api/v1/health/

# Check individual service status
docker-compose -f docker-compose.production.yml ps
```

4. **Performance Issues**
```bash
# Monitor resource usage
docker stats

# Check application metrics
./monitor.sh

# Analyze slow queries
docker-compose -f docker-compose.production.yml exec db psql -U saas_user -d saas_production -c "SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

### 📋 Production Checklist

**Before Deployment:**
- [ ] SECRET_KEY is secure and unique
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured with production domains
- [ ] SSL certificates obtained and configured
- [ ] Database passwords are secure
- [ ] Email configuration tested
- [ ] Backup procedures established
- [ ] Monitoring set up
- [ ] Log rotation configured
- [ ] Firewall rules applied

**After Deployment:**
- [ ] Health checks passing
- [ ] SSL certificate valid
- [ ] Admin panel accessible
- [ ] API endpoints working
- [ ] Email notifications working
- [ ] Backups running successfully
- [ ] Monitoring alerts configured
- [ ] Performance benchmarks met

### 🔐 Government-Level Security Compliance

This application implements security measures suitable for government and enterprise deployments:

#### Security Features
- **Multi-Factor Authentication (MFA)** with TOTP
- **Role-Based Access Control (RBAC)** with hierarchical permissions
- **Attribute-Based Access Control (ABAC)** for context-aware security
- **Account lockout** protection against brute force attacks
- **Comprehensive audit logging** for compliance
- **Session management** with device tracking
- **Password strength** validation and history
- **Rate limiting** and DDoS protection
- **Security headers** and CSP policies
- **Data encryption** at rest and in transit

#### Compliance Standards
- **NIST Cybersecurity Framework** aligned
- **OWASP Top 10** protections implemented
- **SOC 2** compliance ready
- **GDPR** privacy controls included
- **HIPAA** security safeguards available

### 📞 Support

For production support and security questions:
- Create an issue in the repository
- Contact the development team
- Review security documentation
- Check troubleshooting guides

---

**⚠️ Important Security Notice**: This is a production-ready template with government-level security standards. Always review and customize security settings for your specific use case and compliance requirements.

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
