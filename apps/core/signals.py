"""
Core signals for the application
"""
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(pre_save)
def auto_update_version(sender, instance, **kwargs):
    """
    Automatically increment version for audit models
    """
    if hasattr(instance, 'version') and hasattr(instance, 'pk') and instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance:
                instance.version = old_instance.version + 1
        except sender.DoesNotExist:
            pass


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Handle user post-save operations
    """
    if created:
        logger.info(f"New user created: {instance.email}")
        # Additional user setup can be added here
