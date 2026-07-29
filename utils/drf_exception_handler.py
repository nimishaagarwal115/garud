from rest_framework.views import exception_handler as drf_exception_handler
from .drf_response import error_response

def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        errors = response.data
        if isinstance(errors, dict):
            message = errors.get('detail', 'An error occurred')
        elif isinstance(errors, list):
            message = errors[0] if errors else 'An error occurred'
        else:
            message = 'An error occurred'
        return error_response(errors=errors, message=message, status_code=response.status_code)

    return response