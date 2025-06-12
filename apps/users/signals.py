"""
User signals for automatic profile creation and role assignment
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
from apps.permissions.utils import assign_default_role_to_user

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile when a new user is created
    """
    if created:
        try:
            UserProfile.objects.create(user=instance)
            logger.info(f"User profile created for: {instance.email}")
        except Exception as e:
            logger.error(f"Failed to create user profile for {instance.email}: {e}")


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Assign default role to new users
    """
    if created:
        try:
            # Assign default role based on user type
            role_mapping = {
                'admin': 'Administrator',
                'manager': 'Manager',
                'employee': 'Employee',
                'client': 'Client',
                'guest': 'Guest'
            }
            
            default_role = role_mapping.get(instance.user_type, 'Client')
            assign_default_role_to_user(instance, default_role)
            
        except Exception as e:
            logger.error(f"Failed to assign default role to {instance.email}: {e}")


@receiver(pre_save, sender=User)
def update_username_from_email(sender, instance, **kwargs):
    """
    Auto-generate username from email if not provided
    """
    if not instance.username and instance.email:
        # Generate username from email (before @ symbol)
        base_username = instance.email.split('@')[0]
        
        # Ensure username is unique
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exclude(pk=instance.pk).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        instance.username = username
