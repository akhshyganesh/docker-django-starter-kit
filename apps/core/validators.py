"""
Custom password validators for enhanced security
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Validator that enforces password complexity requirements
    """
    
    def __init__(self, min_uppercase=1, min_lowercase=1, min_digits=1, min_special=1):
        self.min_uppercase = min_uppercase
        self.min_lowercase = min_lowercase
        self.min_digits = min_digits
        self.min_special = min_special
        
    def validate(self, password, user=None):
        errors = []
        
        # Check for uppercase letters
        if len(re.findall(r'[A-Z]', password)) < self.min_uppercase:
            errors.append(
                _('Password must contain at least {} uppercase letter(s).'.format(
                    self.min_uppercase
                ))
            )
        
        # Check for lowercase letters
        if len(re.findall(r'[a-z]', password)) < self.min_lowercase:
            errors.append(
                _('Password must contain at least {} lowercase letter(s).'.format(
                    self.min_lowercase
                ))
            )
        
        # Check for digits
        if len(re.findall(r'[0-9]', password)) < self.min_digits:
            errors.append(
                _('Password must contain at least {} digit(s).'.format(
                    self.min_digits
                ))
            )
        
        # Check for special characters
        if len(re.findall(r'[!@#$%^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]', password)) < self.min_special:
            errors.append(
                _('Password must contain at least {} special character(s).'.format(
                    self.min_special
                ))
            )
        
        # Check for common patterns
        if re.search(r'(.)\1{2,}', password):
            errors.append(_('Password cannot contain repeated characters.'))
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            errors.append(_('Password cannot contain sequential characters.'))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            "Your password must contain at least {} uppercase letter, "
            "{} lowercase letter, {} digit, and {} special character. "
            "It cannot contain repeated or sequential characters."
        ).format(
            self.min_uppercase,
            self.min_lowercase, 
            self.min_digits,
            self.min_special
        )


class PreviousPasswordValidator:
    """
    Validator that prevents reusing recent passwords
    """
    
    def __init__(self, history_count=5):
        self.history_count = history_count
    
    def validate(self, password, user=None):
        if user and hasattr(user, 'password_history'):
            # Check against password history
            from django.contrib.auth.hashers import check_password
            
            recent_passwords = user.password_history.order_by('-created_at')[:self.history_count]
            
            for old_password in recent_passwords:
                if check_password(password, old_password.password_hash):
                    raise ValidationError(
                        _('Password cannot be one of your {} most recent passwords.'.format(
                            self.history_count
                        ))
                    )
    
    def get_help_text(self):
        return _(
            "Your password cannot be one of your {} most recent passwords."
        ).format(self.history_count)
