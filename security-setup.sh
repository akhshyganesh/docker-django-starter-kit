#!/bin/bash

# =================================================================
# SECURITY HARDENING SCRIPT FOR PRODUCTION DEPLOYMENT
# =================================================================
# This script applies security hardening measures for production

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Generate secure random secret key
generate_secret_key() {
    log_info "Generating secure secret key..."
    
    if command -v python3 &> /dev/null; then
        SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        echo "Generated SECRET_KEY: $SECRET_KEY"
        log_success "Secret key generated. Please update your .env file with this key."
    else
        log_error "Python3 not found. Please generate a secret key manually."
    fi
}

# Create strong passwords
generate_db_password() {
    log_info "Generating secure database password..."
    
    DB_PASSWORD=$(openssl rand -base64 32)
    echo "Generated DB_PASSWORD: $DB_PASSWORD"
    log_success "Database password generated. Please update your .env file."
}

# Create htpasswd file for Flower monitoring
create_flower_auth() {
    log_info "Creating authentication for Flower monitoring..."
    
    read -p "Enter username for Flower monitoring: " USERNAME
    read -s -p "Enter password for Flower monitoring: " PASSWORD
    echo
    
    # Create htpasswd file
    mkdir -p nginx
    echo "$PASSWORD" | htpasswd -c -i nginx/.htpasswd "$USERNAME"
    
    log_success "Flower authentication created"
}

# Set up log rotation
setup_log_rotation() {
    log_info "Setting up log rotation configuration..."
    
    cat > logrotate.conf << EOF
/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 django django
    postrotate
        docker-compose -f docker-compose.production.yml exec web python manage.py flush_logs
    endscript
}

/app/logs/nginx/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 nginx nginx
    postrotate
        docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
    endscript
}
EOF
    
    log_success "Log rotation configured"
}

# Create backup script
create_backup_script() {
    log_info "Creating backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash

# Database backup script
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME=${POSTGRES_DB:-saas_production}
DB_USER=${POSTGRES_USER:-saas_user}

mkdir -p $BACKUP_DIR

# Database backup
docker-compose -f docker-compose.production.yml exec -T db pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Media files backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz ./mediafiles/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF
    
    chmod +x backup.sh
    log_success "Backup script created"
}

# Create monitoring script
create_monitoring_script() {
    log_info "Creating monitoring script..."
    
    cat > monitor.sh << 'EOF'
#!/bin/bash

# Simple monitoring script
check_services() {
    echo "=== Service Status ==="
    docker-compose -f docker-compose.production.yml ps
    
    echo -e "\n=== Health Check ==="
    curl -s http://localhost/api/v1/health/ | jq '.' 2>/dev/null || echo "Health check failed"
    
    echo -e "\n=== Resource Usage ==="
    docker stats --no-stream
    
    echo -e "\n=== Disk Space ==="
    df -h
    
    echo -e "\n=== Memory Usage ==="
    free -h
}

# Check if services are running
if docker-compose -f docker-compose.production.yml ps | grep -q "Up"; then
    check_services
else
    echo "Services are not running!"
    exit 1
fi
EOF
    
    chmod +x monitor.sh
    log_success "Monitoring script created"
}

# Security checklist
security_checklist() {
    log_info "Production Security Checklist:"
    echo
    echo "✓ 1. Change default SECRET_KEY in .env"
    echo "✓ 2. Set DEBUG=False in .env"  
    echo "✓ 3. Configure proper ALLOWED_HOSTS"
    echo "✓ 4. Set strong database passwords"
    echo "✓ 5. Enable SSL/TLS certificates"
    echo "✓ 6. Configure proper CORS settings"
    echo "✓ 7. Set up monitoring and logging"
    echo "✓ 8. Configure backup procedures"
    echo "✓ 9. Set up log rotation"
    echo "✓ 10. Restrict admin access"
    echo
    echo "Additional recommendations:"
    echo "• Use a proper SSL certificate from a CA"
    echo "• Set up firewall rules"
    echo "• Configure intrusion detection"
    echo "• Regular security updates"
    echo "• Monitor application logs"
    echo "• Set up alerting for critical issues"
    echo
}

# Main security setup
main() {
    echo "==================================================================="
    echo "           PRODUCTION SECURITY HARDENING"
    echo "==================================================================="
    echo
    
    case "${1:-all}" in
        "secrets")
            generate_secret_key
            generate_db_password
            ;;
        "auth")
            create_flower_auth
            ;;
        "logs")
            setup_log_rotation
            ;;
        "backup")
            create_backup_script
            ;;
        "monitor")
            create_monitoring_script
            ;;
        "checklist")
            security_checklist
            ;;
        "all")
            generate_secret_key
            generate_db_password
            create_flower_auth
            setup_log_rotation
            create_backup_script
            create_monitoring_script
            security_checklist
            ;;
        *)
            echo "Usage: $0 {secrets|auth|logs|backup|monitor|checklist|all}"
            echo
            echo "Commands:"
            echo "  secrets   - Generate secure secrets"
            echo "  auth      - Set up authentication"
            echo "  logs      - Configure log rotation"
            echo "  backup    - Create backup script"
            echo "  monitor   - Create monitoring script"
            echo "  checklist - Show security checklist"
            echo "  all       - Run all security setup"
            exit 1
            ;;
    esac
}

main "$@"
