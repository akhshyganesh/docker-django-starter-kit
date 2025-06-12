"""
Custom exception handlers for the API
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    logger.error(f"API Exception: {exc}", exc_info=True, extra={'context': context})
    
    custom_response_data = {
        'error': True,
        'message': 'An error occurred',
        'details': None,
        'error_code': None,
        'timestamp': None
    }
    
    if response is not None:
        if hasattr(exc, 'get_codes') and callable(exc.get_codes):
            custom_response_data['error_code'] = exc.get_codes()
        
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            elif 'non_field_errors' in response.data:
                custom_response_data['message'] = response.data['non_field_errors'][0]
            else:
                custom_response_data['details'] = response.data
        elif isinstance(response.data, list):
            custom_response_data['message'] = response.data[0] if response.data else 'An error occurred'
        else:
            custom_response_data['message'] = str(response.data)
            
        response.data = custom_response_data
        
    else:
        # Handle non-DRF exceptions
        if isinstance(exc, Http404):
            custom_response_data['message'] = 'Resource not found'
            custom_response_data['error_code'] = 'not_found'
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data['message'] = 'Permission denied'
            custom_response_data['error_code'] = 'permission_denied'
            response = Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)
            
        elif isinstance(exc, ValidationError):
            custom_response_data['message'] = 'Validation error'
            custom_response_data['details'] = exc.message_dict if hasattr(exc, 'message_dict') else str(exc)
            custom_response_data['error_code'] = 'validation_error'
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, IntegrityError):
            custom_response_data['message'] = 'Database integrity error'
            custom_response_data['error_code'] = 'integrity_error'
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            custom_response_data['message'] = 'Internal server error'
            custom_response_data['error_code'] = 'internal_error'
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response
