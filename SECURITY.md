# Security Configuration Guide

## Production Security Checklist

### ✅ Authentication & Authorization
- [x] Multi-factor authentication (MFA) implemented
- [x] Firebase authentication integration
- [x] JWT token authentication with Knox
- [x] Role-based access control (RBAC)
- [x] Attribute-based access control (ABAC)
- [x] Strong password policies (12+ characters, complexity)
- [x] Account lockout protection (3 attempts, 2-hour cooldown)

### ✅ Network Security
- [x] Rate limiting on all endpoints
- [x] IP whitelist for admin access
- [x] CORS properly configured
- [x] Security headers implemented
- [x] Content Security Policy (CSP) configured
- [x] No SSL/TLS required (direct deployment)

### ✅ Data Protection
- [x] Database connection security
- [x] Redis connection security
- [x] Session security (HTTPOnly, Secure when needed)
- [x] CSRF protection enabled
- [x] XSS protection headers
- [x] Audit logging for all critical operations

### ✅ Application Security
- [x] Django security middleware enabled
- [x] Debug mode disabled in production
- [x] Secret key properly configured
- [x] Static files served securely via WhiteNoise
- [x] Input validation and sanitization
- [x] SQL injection protection via ORM

### ✅ Monitoring & Logging
- [x] Comprehensive audit logging
- [x] Security event monitoring
- [x] Failed login attempt tracking
- [x] Suspicious activity detection
- [x] Sentry integration for error tracking
- [x] Health check endpoints

## Security Configuration Details

### Rate Limiting
```python
# Authentication endpoints: 10 requests/minute
# API endpoints: 100 requests/minute  
# General endpoints: 200 requests/minute
```

### Admin Access Control
- Only accessible from whitelisted IPs
- Default: 127.0.0.1, ::1
- Configure via ADMIN_ALLOWED_IPS environment variable

### Session Security
```python
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Strict'
```

### CSRF Protection
```python
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
```

### Content Security Policy
```
default-src 'self';
script-src 'self';
style-src 'self';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
form-action 'self';
base-uri 'self';
object-src 'none';
```

## Production Environment Variables

### Required Security Variables
```bash
# Core Security
SECRET_KEY=your-complex-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ip-address
CSRF_TRUSTED_ORIGINS=https://your-domain.com

# Admin Security
ADMIN_ALLOWED_IPS=your-admin-ip-addresses

# Rate Limiting
RATELIMIT_ENABLE=True

# Monitoring
SENTRY_DSN=your-sentry-dsn-for-error-tracking
```

## Security Endpoints

### Health Check
```
GET /health/
```
Returns application health status

### Security Headers Test
```
GET /security-test/
```
Verifies security headers are properly configured

## Security Incident Response

### Account Lockout
- Automatic lockout after 3 failed attempts
- 2-hour cooldown period
- Admin can manually unlock accounts
- All attempts are logged

### Suspicious Activity Detection
- SQL injection attempts
- XSS attempts
- Automated scanning tools
- Unusual user agent strings
- All incidents logged to security log

### Rate Limiting
- HTTP 429 response for exceeded limits
- Automatic IP-based throttling
- Different limits for different endpoint types

## Deployment Security Notes

### Direct Deployment (No Reverse Proxy)
- Django serves directly via Gunicorn
- WhiteNoise handles static files
- Built-in security middleware stack
- No SSL termination required at application level
- Rate limiting handled at application level

### Recommended Production Setup
1. Deploy behind a load balancer with SSL termination
2. Use environment-specific configuration
3. Regular security updates and patches
4. Monitor logs for security events
5. Regular backup and disaster recovery testing

### Security Maintenance
- Regular dependency updates
- Security audit logs review
- Failed login monitoring
- Rate limit threshold monitoring
- Performance impact assessment

## Common Security Issues & Solutions

### Issue: High number of failed logins
**Solution**: Check AXES logs, consider IP blocking, review authentication flow

### Issue: Rate limit exceeded frequently
**Solution**: Analyze traffic patterns, adjust limits if legitimate traffic

### Issue: CSRF failures
**Solution**: Verify CSRF_TRUSTED_ORIGINS configuration, check client implementation

### Issue: Session timeouts
**Solution**: Review SESSION_COOKIE_AGE setting, implement proper session refresh

### Issue: Suspicious activity alerts
**Solution**: Investigate source IPs, patterns, implement additional filtering if needed

## Gunicorn Security Configuration

### Optimized Production Settings
The application uses an optimized Gunicorn configuration file (`gunicorn.conf.py`) with the following security enhancements:

#### Worker Configuration
```python
# Dynamic worker scaling based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000  # Restart workers after handling 1000 requests
max_requests_jitter = 50  # Add randomness to avoid thundering herd
```

#### Security Limits
```python
# Request size limits to prevent abuse
limit_request_line = 4094      # Maximum size of HTTP request line
limit_request_fields = 100     # Maximum number of header fields
limit_request_field_size = 8190 # Maximum size of header field
```

#### Process Security
```python
# Process isolation and monitoring
preload_app = True              # Preload application for better performance
timeout = 30                   # Worker timeout in seconds
graceful_timeout = 30          # Graceful shutdown timeout
proc_name = "django_app"       # Process name for monitoring
```

#### Logging Configuration
```python
# Comprehensive security logging
accesslog = "/app/logs/gunicorn_access.log"
errorlog = "/app/logs/gunicorn_error.log"
loglevel = "info"
# Detailed access log format including response time
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
```

#### Performance & Security Optimizations
```python
# Memory optimization
worker_tmp_dir = "/dev/shm"    # Use shared memory for temporary files
keepalive = 2                  # HTTP keep-alive connections
backlog = 2048                 # Maximum number of pending connections
```

## Container Security

### Docker Security Best Practices
- [x] **Non-root user**: Application runs as `django` user (UID/GID isolation)
- [x] **Minimal base image**: Using `python:3.11-slim-bullseye` for reduced attack surface
- [x] **Security updates**: Regular base image updates for security patches
- [x] **Resource limits**: Configurable CPU and memory limits via Docker Compose
- [x] **Read-only filesystem**: Application files mounted read-only where possible
- [x] **Network isolation**: Services isolated via Docker networks

### Container Runtime Security
```dockerfile
# Security-focused Dockerfile optimizations
RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django /app
USER django  # Switch to non-root user

# Proper file permissions
RUN chmod +x /app/entrypoint.sh
RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs
```

### Environment-Based Configuration
The entrypoint script automatically detects production environment:
```bash
if [ "$DJANGO_ENV" = "production" ]; then
    # Use optimized Gunicorn configuration
    exec gunicorn core.wsgi:application --config /app/gunicorn.conf.py
else
    # Development server for local development
    exec python manage.py runserver 0.0.0.0:8000
fi
```

## Advanced Security Monitoring

### Log Analysis Patterns
Monitor these patterns in Gunicorn logs for security threats:

#### Suspicious Request Patterns
```bash
# Large request attempts (potential DoS)
grep "request line too large" /app/logs/gunicorn_error.log

# Too many header fields (potential header injection)
grep "too many header fields" /app/logs/gunicorn_error.log

# Worker timeouts (potential resource exhaustion)
grep "timeout" /app/logs/gunicorn_error.log
```

#### Performance Monitoring
```bash
# Monitor response times
awk '{print $NF}' /app/logs/gunicorn_access.log | sort -n | tail -10

# Monitor error rates
grep " 5[0-9][0-9] " /app/logs/gunicorn_access.log | wc -l
```

### Security Alerting Thresholds
- **High error rate**: >5% 5xx responses in 5 minutes
- **Slow responses**: >50% requests taking >5 seconds
- **Worker restarts**: >10 worker restarts per hour
- **Memory usage**: >80% container memory utilization
