from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
# from .permissions import IsAuthenticatedWithCurrentBusiness
from .drf_response import success_response, error_response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser

class BaseViewSet(ModelViewSet):
    """
    Base ViewSet to handle common response patterns and delegate business logic to service classes.
    """
    permission_classes = [AllowAny]  # Default permission class
    filter_backends = [DjangoFilterBackend, SearchFilter]  # Default filter backends
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get_serializer(self, *args, **kwargs):
        """
        Override to support dynamic fields selection by adding fields to the context.
        """
        # Get the fields parameter from the query params
        fields = self.request.query_params.get('fields', None)
        
        # Add fields to the serializer context
        context = self.get_serializer_context()
        if fields:
            context['fields'] = fields.split(',')
        
        # Pass the updated context to the serializer
        kwargs['context'] = context
        return self.serializer_class(*args, **kwargs)

    def get_queryset(self):
        """
        Dynamically retrieve the queryset based on the service class and user role.
        """
        try:
            if not hasattr(self, 'service_class') or not self.service_class:
                raise AttributeError("The 'service_class' attribute must be defined in the viewset.")

            # Delegate to the service class to retrieve the queryset
            return self.service_class.get_all(self.request)
        except ValidationError as e:
            raise ValidationError(f"Validation error in BaseViewSet get_queryset: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error in BaseViewSet get_queryset: {e}")

    def retrieve(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a single record.
        Uses the service_class.get method if implemented, otherwise falls back to default behavior.
        """
        try:
            # Check if the service_class has a `get` method
            if hasattr(self.service_class, 'get') and callable(getattr(self.service_class, 'get')):
                # Use the service_class.get method to fetch the object
                instance = self.service_class.get(kwargs['pk'], request)
            else:
                # Fallback to the default behavior
                instance = self.get_object()

            # Serialize the instance and return a success response
            serializer = self.get_serializer(instance)
            return success_response(serializer.data, message=f"{self.queryset.model.__name__} retrieved successfully.")
        except Exception as e:
            return error_response(errors=str(e), message=f"Failed to retrieve {self.queryset.model.__name__}.")

    def create(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new record.
        """
        try:
            instance = self.service_class.create(request.data, request)
            serializer = self.get_serializer(instance, many=True if isinstance(instance, list) else False)
            return success_response(serializer.data, message=f"{self.queryset.model.__name__} created successfully.", status_code=201)
        except Exception as e:
            return error_response(errors=str(e), message=f"Failed to create {self.queryset.model.__name__}.")

    def update(self, request, *args, **kwargs):
        """
        Handles PATCH requests to update an existing record.
        """
        try:
            instance = self.service_class.update(kwargs['pk'], request.data, request)
            serializer = self.get_serializer(instance)
            return success_response(serializer.data, message=f"{self.queryset.model.__name__} updated successfully.")
        except Exception as e:
            return error_response(errors=str(e), message=f"Failed to update {self.queryset.model.__name__}.")

    def destroy(self, request, *args, **kwargs):
        """
        Handles DELETE requests to delete a record.
        """
        try:
            self.service_class.delete(kwargs['pk'], request)
            return success_response(message=f"{self.queryset.model.__name__} deleted successfully.")
        except Exception as e:
            return error_response(errors=str(e), message=f"Failed to delete {self.queryset.model.__name__}.")

    def list(self, request, *args, **kwargs):
        """
        Handles GET requests to list all records.
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return success_response(serializer.data, message=f"{self.queryset.model.__name__}s retrieved successfully.")
        except NotFound as e:
            return error_response(errors=str(e), message="Invalid page requested.", status_code=400)
        except Exception as e:
            return error_response(errors=str(e), message=f"Failed to retrieve {self.queryset.model.__name__}s.")