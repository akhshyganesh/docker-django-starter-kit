#!/bin/bash

# =================================================================
# PRODUCTION READINESS VALIDATION SCRIPT
# =================================================================
# This script validates that the application is ready for production

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

log_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

log_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

log_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

check_env_file() {
    echo "=== Environment Configuration ==="
    
    if [[ -f ".env" ]]; then
        log_pass ".env file exists"
        
        # Check critical settings
        if grep -q "DEBUG=False" .env; then
            log_pass "DEBUG is set to False"
        else
            log_fail "DEBUG must be set to False for production"
        fi
        
        if grep -q "SECRET_KEY=django-insecure" .env; then
            log_fail "SECRET_KEY is using default insecure value"
        else
            log_pass "SECRET_KEY appears to be customized"
        fi
        
        if grep -q "your-domain.com" .env; then
            log_warn "Default domain found - update ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS"
        else
            log_pass "Domain configuration appears customized"
        fi
        
        if grep -q "POSTGRES_PASSWORD=postgres" .env; then
            log_fail "Database is using default password"
        else
            log_pass "Database password appears secure"
        fi
        
    else
        log_fail ".env file not found - copy from .env.example"
    fi
    echo
}

check_docker_files() {
    echo "=== Docker Configuration ==="
    
    required_files=(
        "docker-compose.production.yml"
        "Dockerfile.production"
        "nginx/nginx.production.conf"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_pass "$file exists"
        else
            log_fail "$file not found"
        fi
    done
    echo
}

check_ssl_certificates() {
    echo "=== SSL Configuration ==="
    
    if [[ -f "nginx/ssl/cert.pem" ]] && [[ -f "nginx/ssl/key.pem" ]]; then
        log_pass "SSL certificates found"
        
        # Check certificate validity
        if openssl x509 -in nginx/ssl/cert.pem -checkend 86400 -noout >/dev/null 2>&1; then
            log_pass "SSL certificate is valid"
        else
            log_warn "SSL certificate expires within 24 hours"
        fi
        
        # Check if self-signed
        if openssl x509 -in nginx/ssl/cert.pem -text -noout | grep -q "CN=localhost"; then
            log_warn "Using self-signed certificate (OK for testing, replace for production)"
        else
            log_pass "Using proper SSL certificate"
        fi
    else
        log_fail "SSL certificates not found in nginx/ssl/"
    fi
    echo
}

check_scripts() {
    echo "=== Deployment Scripts ==="
    
    scripts=("deploy.sh" "security-setup.sh")
    
    for script in "${scripts[@]}"; do
        if [[ -f "$script" ]] && [[ -x "$script" ]]; then
            log_pass "$script is executable"
        elif [[ -f "$script" ]]; then
            log_warn "$script exists but is not executable (run: chmod +x $script)"
        else
            log_fail "$script not found"
        fi
    done
    echo
}

check_security_settings() {
    echo "=== Security Configuration ==="
    
    # Check file permissions
    if [[ -f ".env" ]]; then
        perms=$(stat -f "%A" .env 2>/dev/null || stat -c "%a" .env 2>/dev/null)
        if [[ "$perms" == "600" ]]; then
            log_pass ".env file has secure permissions (600)"
        else
            log_warn ".env file permissions should be 600 (run: chmod 600 .env)"
        fi
    fi
    
    # Check SSL directory permissions
    if [[ -d "nginx/ssl" ]]; then
        perms=$(stat -f "%A" nginx/ssl 2>/dev/null || stat -c "%a" nginx/ssl 2>/dev/null)
        if [[ "$perms" == "700" ]]; then
            log_pass "SSL directory has secure permissions (700)"
        else
            log_warn "SSL directory permissions should be 700 (run: chmod 700 nginx/ssl)"
        fi
    fi
    
    echo
}

check_production_requirements() {
    echo "=== Production Requirements ==="
    
    if [[ -f "requirements.production.txt" ]]; then
        log_pass "Production requirements file exists"
    else
        log_warn "Consider using requirements.production.txt for production dependencies"
    fi
    
    if [[ -f "core/production_settings.py" ]]; then
        log_pass "Production settings file exists"
    else
        log_warn "Consider using separate production settings"
    fi
    
    echo
}

check_monitoring() {
    echo "=== Monitoring Setup ==="
    
    if [[ -f "apps/core/health.py" ]]; then
        log_pass "Health check endpoints available"
    else
        log_warn "Health check endpoints not found"
    fi
    
    if grep -q "SENTRY_DSN" .env 2>/dev/null; then
        log_pass "Sentry monitoring configured"
    else
        log_warn "Consider setting up error monitoring (Sentry)"
    fi
    
    echo
}

show_summary() {
    echo "==================================================================="
    echo "                      VALIDATION SUMMARY"
    echo "==================================================================="
    echo
    echo -e "${GREEN}Passed: $PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Failed: $FAILED${NC}"
    echo
    
    if [[ $FAILED -eq 0 ]]; then
        echo -e "${GREEN}🎉 Production readiness validation passed!${NC}"
        if [[ $WARNINGS -gt 0 ]]; then
            echo -e "${YELLOW}⚠️  Address warnings before production deployment${NC}"
        fi
        echo
        echo "Next steps:"
        echo "1. Review warnings and address if needed"
        echo "2. Test deployment: ./deploy.sh deploy"
        echo "3. Verify health checks: curl https://your-domain.com/api/v1/health/"
        echo "4. Set up monitoring and backups"
    else
        echo -e "${RED}❌ Production readiness validation failed!${NC}"
        echo "Please fix the failed checks before deploying to production."
    fi
    echo
}

main() {
    echo "==================================================================="
    echo "              PRODUCTION READINESS VALIDATION"
    echo "==================================================================="
    echo
    
    check_env_file
    check_docker_files
    check_ssl_certificates
    check_scripts
    check_security_settings
    check_production_requirements
    check_monitoring
    show_summary
    
    # Exit with error if there are failures
    if [[ $FAILED -gt 0 ]]; then
        exit 1
    fi
}

main "$@"
