#!/bin/bash

# =================================================================
# PRODUCTION DEPLOYMENT SCRIPT
# =================================================================
# This script handles secure production deployment with proper checks

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check if required files exist
check_requirements() {
    log_info "Checking deployment requirements..."
    
    required_files=(
        ".env"
        "docker-compose.production.yml"
        "Dockerfile.production"
        "nginx/nginx.production.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    
    log_success "All required files present"
}

# Validate environment variables
validate_env() {
    log_info "Validating environment configuration..."
    
    # Check if .env file has production settings
    if grep -q "DEBUG=True" .env; then
        log_error "DEBUG is set to True in .env file. This must be False for production!"
        exit 1
    fi
    
    if grep -q "SECRET_KEY=django-insecure" .env; then
        log_error "Default insecure SECRET_KEY detected. Please generate a secure secret key!"
        exit 1
    fi
    
    if grep -q "your-domain.com" .env; then
        log_warning "Default domain detected in .env. Please update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS"
    fi
    
    log_success "Environment validation passed"
}

# Generate SSL certificates (self-signed for testing)
generate_ssl_certs() {
    log_info "Checking SSL certificates..."
    
    if [[ ! -f "nginx/ssl/cert.pem" ]] || [[ ! -f "nginx/ssl/key.pem" ]]; then
        log_warning "SSL certificates not found. Generating self-signed certificates for testing..."
        
        mkdir -p nginx/ssl
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        log_warning "Self-signed certificates generated. Please replace with proper SSL certificates for production!"
    else
        log_success "SSL certificates found"
    fi
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    directories=(
        "logs"
        "logs/nginx"
        "staticfiles"
        "mediafiles"
        "nginx/ssl"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
    done
    
    log_success "Directories created"
}

# Set proper permissions
set_permissions() {
    log_info "Setting proper file permissions..."
    
    # Make scripts executable
    chmod +x entrypoint.sh
    chmod +x wait_for_db.py
    
    # Set secure permissions for sensitive files
    if [[ -f ".env" ]]; then
        chmod 600 .env
    fi
    
    if [[ -d "nginx/ssl" ]]; then
        chmod 700 nginx/ssl
        find nginx/ssl -type f -exec chmod 600 {} \;
    fi
    
    log_success "Permissions set"
}

# Build and start production services
deploy_production() {
    log_info "Building and starting production services..."
    
    # Pull latest images
    docker-compose -f docker-compose.production.yml pull
    
    # Build custom images
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Start services
    docker-compose -f docker-compose.production.yml up -d
    
    log_success "Production services started"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to be healthy..."
    
    max_attempts=30
    attempt=0
    
    while [[ $attempt -lt $max_attempts ]]; do
        if curl -f http://localhost/api/v1/health/ &>/dev/null; then
            log_success "All services are healthy"
            return 0
        fi
        
        ((attempt++))
        log_info "Attempt $attempt/$max_attempts - waiting for services..."
        sleep 10
    done
    
    log_error "Services failed to become healthy within expected time"
    return 1
}

# Run database migrations and setup
setup_database() {
    log_info "Setting up database..."
    
    # Run migrations
    docker-compose -f docker-compose.production.yml exec web python manage.py migrate --noinput
    
    # Create default permissions
    docker-compose -f docker-compose.production.yml exec web python manage.py create_default_permissions
    
    # Collect static files
    docker-compose -f docker-compose.production.yml exec web python manage.py collectstatic --noinput --clear
    
    log_success "Database setup completed"
}

# Security check
security_check() {
    log_info "Running security checks..."
    
    # Check Django security
    docker-compose -f docker-compose.production.yml exec web python manage.py check --deploy
    
    log_success "Security checks passed"
}

# Display deployment information
show_deployment_info() {
    log_success "Deployment completed successfully!"
    echo
    echo "==================================================================="
    echo "                    DEPLOYMENT INFORMATION"
    echo "==================================================================="
    echo
    echo "Application URL: https://localhost"
    echo "API Documentation: https://localhost/api/docs/"
    echo "Admin Panel: https://localhost/admin/"
    echo "Health Check: https://localhost/api/v1/health/"
    echo
    echo "Monitoring:"
    echo "- Flower (Celery): https://localhost/flower/"
    echo "- Logs: docker-compose -f docker-compose.production.yml logs -f"
    echo
    echo "Management Commands:"
    echo "- View logs: docker-compose -f docker-compose.production.yml logs -f [service]"
    echo "- Scale services: docker-compose -f docker-compose.production.yml up -d --scale web=3"
    echo "- Stop services: docker-compose -f docker-compose.production.yml down"
    echo
    echo "==================================================================="
    echo
    log_warning "Remember to:"
    echo "1. Replace self-signed SSL certificates with proper ones"
    echo "2. Configure proper domain names in nginx configuration"
    echo "3. Set up proper monitoring and backup procedures"
    echo "4. Review and update security settings for your environment"
}

# Main deployment process
main() {
    echo "==================================================================="
    echo "           PRODUCTION DJANGO DEPLOYMENT SCRIPT"
    echo "==================================================================="
    echo
    
    check_root
    check_requirements
    validate_env
    create_directories
    generate_ssl_certs
    set_permissions
    deploy_production
    
    if wait_for_services; then
        setup_database
        security_check
        show_deployment_info
    else
        log_error "Deployment failed - services are not healthy"
        docker-compose -f docker-compose.production.yml logs
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping production services..."
        docker-compose -f docker-compose.production.yml down
        log_success "Services stopped"
        ;;
    "logs")
        docker-compose -f docker-compose.production.yml logs -f "${2:-}"
        ;;
    "status")
        docker-compose -f docker-compose.production.yml ps
        ;;
    "backup")
        log_info "Creating database backup..."
        docker-compose -f docker-compose.production.yml exec db pg_dump -U saas_user saas_production > "backup_$(date +%Y%m%d_%H%M%S).sql"
        log_success "Database backup created"
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs|status|backup}"
        echo
        echo "Commands:"
        echo "  deploy  - Deploy the application to production"
        echo "  stop    - Stop all production services"
        echo "  logs    - View logs (optionally specify service name)"
        echo "  status  - Show status of all services"
        echo "  backup  - Create database backup"
        exit 1
        ;;
esac
