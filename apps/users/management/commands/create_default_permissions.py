"""
Management command to create default permissions and roles
"""
from django.core.management.base import BaseCommand
from apps.permissions.utils import create_default_permissions, create_default_roles


class Command(BaseCommand):
    help = 'Create default permissions and roles'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating default permissions...')
        permissions = create_default_permissions()
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(permissions)} permissions')
        )
        
        self.stdout.write('Creating default roles...')
        roles = create_default_roles()
        self.stdout.write(
            self.style.SUCCESS(f'Created {len(roles)} roles')
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created default permissions and roles')
        )
