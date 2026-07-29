from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def business_required(view_func):
    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        if request.user.get_business() is None:
            return Response({"error": "User must have an associated business."}, status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, *args, **kwargs)
    return _wrapped_view