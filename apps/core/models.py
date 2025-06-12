"""
Base models for the application
"""
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class BaseModel(models.Model):
    """
    Abstract base model with common fields
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated'
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.__class__.__name__} - {self.id}"


class AuditModel(BaseModel):
    """
    Extended base model with audit fields
    """
    version = models.PositiveIntegerField(default=1)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted'
    )
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None):
        """Soft delete the record"""
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.is_active = False
        self.save()
    
    def restore(self, user=None):
        """Restore a soft-deleted record"""
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
        self.updated_by = user
        self.save()
    
    @property
    def is_deleted(self):
        return self.deleted_at is not None
