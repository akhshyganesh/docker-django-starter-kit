"""
Permissions application configuration
"""
from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.permissions'
    verbose_name = 'Permissions'
    
    def ready(self):
        """Initialize default permissions and roles"""
        try:
            from apps.permissions.utils import create_default_permissions
            create_default_permissions()
        except Exception:
            # Ignore during migrations
            pass
