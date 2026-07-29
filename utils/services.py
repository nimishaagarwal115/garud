from django.shortcuts import get_object_or_404
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models.fields.related import ForeignKey

class BaseService:
    model = None  # Define the model class in child classes
    serializer_class = None  # Define the serializer class in child classes

    @classmethod
    def get(cls, pk, request=None, business_field=None):
        """
        Retrieve a single object by primary key and validate business access.
        :param pk: Primary key of the object.
        :param request: The request object (optional).
        :param business_field: Custom path to the Business object (e.g., 'checkpoint.business_site.business').
        """
        instance = get_object_or_404(cls.model, pk=pk)        
        return instance

    @classmethod
    def get_all(cls, request=None, filters=None):
        """Retrieve all objects, optionally filtered."""
        queryset = cls.model.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        # if request and hasattr(cls.model, 'business'):
        #     queryset = queryset.filter(business=request.current_business)
        return queryset

    @classmethod
    @transaction.atomic
    def create(cls, data, request=None):
        """Create a new object."""
        serializer = cls.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    @transaction.atomic
    def update(cls, pk, data, request=None, business_field=None):
        """Update an existing object."""
        instance = cls.get(pk, request, business_field)
        serializer = cls.serializer_class(instance, data=data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @classmethod
    @transaction.atomic
    def delete(cls, pk, request=None, business_field=None):
        """Delete an object."""
        instance = cls.get(pk, request, business_field)
        instance.delete()
        return {"message": f"{cls.model.__name__} deleted successfully."}

    