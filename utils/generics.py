from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status
import traceback, json

def success_response(message = None, data=None, status_code = 200):
    try:
        if status_code == 200:
            status_code = status.HTTP_200_OK
        elif status_code == 201:
            status_code = status.HTTP_201_CREATED
        elif status_code == 204:
            status_code = status.HTTP_204_NO_CONTENT

        return Response({
            "status": "success",
            "message": message or "Success",
            "data": data or message or []
        }, status=status_code)
    except Exception as e:
        traceback.print_exc()
        print(str(e))


def error_response(message, errors=None, status_code=status.HTTP_400_BAD_REQUEST, trace=True, data=None):
    if not isinstance(message, str):
        message = str(message)
    elif errors and not isinstance(errors, str):
        errors = str(errors)

    if "--" in message:
        message, code = message.split("--")
        code = int(code.strip())
        if code == 401:
            status_code = status.HTTP_401_UNAUTHORIZED
        elif code == 403:
            status_code = status.HTTP_403_FORBIDDEN
        elif code == 404:
            status_code = status.HTTP_404_NOT_FOUND
        elif code == 405:
            status_code = status.HTTP_405_METHOD_NOT_ALLOWED
        elif status_code == 204:
            status_code = status.HTTP_204_NO_CONTENT
        else:
            status_code = status.HTTP_400_BAD_REQUEST

    if "||" in message:
        message, errors = message.split("||")
        
    if trace:
        traceback.print_exc()

    # Build the response object
    response = {
        "status": "error",
        "message": message,
        "errors": errors or message,
    }

    # Include data if provided
    if data is not None:
        response["data"] = data

    return Response(response, status=status_code)

def jsonify_from_string(data):
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return None
    

def searchQueryset(queryset, fields, searchTerm):          
    # Initialize an empty Q object to build the OR conditions
    search_filter = Q()
    for field in fields:
        # Construct the lookup expression dynamically using field names
        if '__' in field:
            # Split the field by '__' to get the ForeignKey field and the related field
            foreign_key_field, related_field = field.split('__', 1)
            # Construct the lookup expression dynamically for the related field
            lookup_expr = f"{foreign_key_field}__{related_field}__icontains"
        else:
            # If no '__' is present, use the field directly
            lookup_expr = f"{field}__icontains"
        # Add the condition to the Q object with OR operator
        search_filter |= Q(**{lookup_expr: searchTerm})    
    # Apply the filter to the initial queryset and return the result    
    return queryset.filter(search_filter)