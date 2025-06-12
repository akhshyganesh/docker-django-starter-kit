"""
Celery tasks for user management
"""
import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.permissions.utils import cleanup_expired_permissions

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def cleanup_inactive_users():
    """
    Clean up inactive users who haven't logged in for a long time
    """
    # Users who haven't logged in for 6 months
    six_months_ago = timezone.now() - timedelta(days=180)
    
    inactive_users = User.objects.filter(
        last_login__lt=six_months_ago,
        is_active=True,
        account_status='active'
    ).exclude(is_staff=True)
    
    count = 0
    for user in inactive_users:
        user.account_status = 'inactive'
        user.is_active = False
        user.save()
        count += 1
        logger.info(f"Deactivated inactive user: {user.email}")
    
    logger.info(f"Cleanup completed. Deactivated {count} inactive users.")
    return f"Deactivated {count} inactive users"


@shared_task
def unlock_locked_accounts():
    """
    Unlock accounts that have passed their lock period
    """
    now = timezone.now()
    
    locked_users = User.objects.filter(
        locked_until__lt=now,
        account_status='locked'
    )
    
    count = 0
    for user in locked_users:
        user.unlock_account()
        count += 1
        logger.info(f"Auto-unlocked user account: {user.email}")
    
    logger.info(f"Auto-unlocked {count} user accounts.")
    return f"Auto-unlocked {count} user accounts"


@shared_task
def cleanup_expired_sessions():
    """
    Clean up expired user sessions
    """
    from apps.users.models import UserSession
    
    now = timezone.now()
    
    expired_sessions = UserSession.objects.filter(
        expires_at__lt=now,
        is_active=True
    )
    
    count = expired_sessions.update(is_active=False)
    
    logger.info(f"Cleaned up {count} expired sessions.")
    return f"Cleaned up {count} expired sessions"


@shared_task
def cleanup_old_audit_logs():
    """
    Clean up old audit logs (keep last 1 year)
    """
    from apps.permissions.models import AuditLog
    
    one_year_ago = timezone.now() - timedelta(days=365)
    
    old_logs = AuditLog.objects.filter(timestamp__lt=one_year_ago)
    count = old_logs.count()
    old_logs.delete()
    
    logger.info(f"Cleaned up {count} old audit logs.")
    return f"Cleaned up {count} old audit logs"


@shared_task
def cleanup_expired_permissions_task():
    """
    Clean up expired permissions and roles
    """
    try:
        cleanup_expired_permissions()
        return "Expired permissions cleanup completed"
    except Exception as e:
        logger.error(f"Failed to cleanup expired permissions: {e}")
        return f"Failed to cleanup expired permissions: {e}"


@shared_task
def send_password_expiry_notifications():
    """
    Send notifications to users whose passwords are about to expire
    """
    # Passwords expire after 90 days
    ninety_days_ago = timezone.now() - timedelta(days=90)
    seven_days_from_now = timezone.now() + timedelta(days=7)
    
    users_with_expiring_passwords = User.objects.filter(
        password_changed_at__lt=ninety_days_ago,
        is_active=True
    )
    
    count = 0
    for user in users_with_expiring_passwords:
        # In a real application, you would send an email here
        logger.info(f"Password expiring soon for user: {user.email}")
        count += 1
    
    logger.info(f"Sent password expiry notifications to {count} users.")
    return f"Sent password expiry notifications to {count} users"


@shared_task
def generate_security_report():
    """
    Generate daily security report
    """
    from apps.permissions.models import AuditLog
    from django.db.models import Count
    
    now = timezone.now()
    yesterday = now - timedelta(days=1)
    
    # Get security metrics for the last 24 hours
    failed_logins = AuditLog.objects.filter(
        action_type='access_denied',
        timestamp__gte=yesterday,
        success=False
    ).count()
    
    successful_logins = AuditLog.objects.filter(
        action_type='access_granted',
        timestamp__gte=yesterday,
        success=True
    ).count()
    
    locked_accounts = User.objects.filter(
        account_status='locked',
        locked_until__gte=yesterday
    ).count()
    
    report = {
        'date': yesterday.date(),
        'failed_logins': failed_logins,
        'successful_logins': successful_logins,
        'locked_accounts': locked_accounts,
        'success_rate': round((successful_logins / (successful_logins + failed_logins)) * 100, 2) if (successful_logins + failed_logins) > 0 else 100
    }
    
    logger.info(f"Security report generated: {report}")
    
    # In a real application, you would send this report via email
    # or store it in a database for dashboard display
    
    return report
