from rest_framework import serializers
from django.db.models import ForeignKey, FileField, ImageField 
from phonenumber_field.modelfields import PhoneNumberField
from urllib.parse import urljoin
from django.db.models import DateTimeField, DateField, TimeField
from datetime import datetime
from django.utils.timezone import localtime
from django.utils.timezone import get_current_timezone
import traceback

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A base serializer that supports dynamic fields and nested fields for all models,
    including reverse relationships (related_name).
    """
    def __init__(self, *args, **kwargs):
        # Print the context for debugging        
        # Get fields from context if available, otherwise use kwargs
        fields = kwargs.get('context', {}).get('fields', None)
        super().__init__(*args, **kwargs)

        if fields:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)
                
                
    def get_nested_serializer(self, related_model):
        """
        Dynamically create a serializer for the related model.
        """
        class NestedSerializer(DynamicFieldsModelSerializer):
            class Meta:
                model = related_model
                fields = '__all__'
            
        return NestedSerializer

    def to_representation(self, instance):
        """
        Custom representation to handle dynamic fields and nested fields, including reverse relationships.
        """
        try:
            representation = super().to_representation(instance)
            request = self.context.get('request', None)
            fields = self.context.get('fields', None)        
            
            # Combine forward and reverse relationships
            relationships = {
                field.name: field for field in instance._meta.get_fields()
                if field.is_relation  # Include all relationships
            }        
            # Add reverse relationships from related_objects
            reverse_relationships = {   
                rel.get_accessor_name(): rel for rel in instance._meta.related_objects
            }
            relationships.update(reverse_relationships)  # Merge forward and reverse relationships

            # Debug: Log reverse relationships
            # relationships = [key.removesuffix('_set') for key in relationships.keys()]        
            relationships_keys = [key for key in relationships.keys()]  
            
            if not fields:
                fields = [
                    field.name for field in instance._meta.get_fields()
                    if field.name not in relationships_keys
                ]        
            
            # Group nested fields by their parent field
            grouped_fields = {}
            for field in fields or []:
                if '__' in field:
                    field_name, nested_field = field.split('__', 1)
                    if field_name not in grouped_fields:
                        grouped_fields[field_name] = []
                    grouped_fields[field_name].append(nested_field)
                else:
                    grouped_fields[field] = [] if field in list(relationships_keys) else None

            # Debug: Log the grouped fields
            # print(f"Grouped fields:{instance} - {grouped_fields}")        

            # Process grouped fields
            for field_name, nested_fields in grouped_fields.items():
                if field_name in list(relationships_keys):
                    related_manager = getattr(instance, field_name, None)  
                    
                    if related_manager and hasattr(related_manager, 'all'):   # Reverse relationship manager
                        related_queryset = related_manager.all() 
                        related_model = relationships[field_name].related_model
                        nested_serializer_class = self.get_nested_serializer(related_model)
                        field_names = nested_fields
                        if not field_names:
                            field_names = [
                                field.name for field in related_model._meta.get_fields() 
                                if not (field.many_to_one or field.one_to_many or field.many_to_many)
                            ]                
                        nested_serializer = nested_serializer_class(
                            related_queryset,
                            many=True,
                            context={**self.context, 'fields': field_names}
                        )
                        
                        representation[field_name] = nested_serializer.data    
                    elif related_manager:  # Direct relationship (e.g., ForeignKey)
                        related_model = relationships[field_name].related_model
                        nested_serializer_class = self.get_nested_serializer(related_model)
                        if nested_fields:
                            nested_serializer = nested_serializer_class(
                                related_manager,
                                context={**self.context, 'fields': nested_fields}
                            )
                            representation[field_name] = nested_serializer.data
                        else:
                            representation[field_name] = related_manager.pk if type(related_manager) is not int else related_manager
                    else:
                        representation[field_name] = None
                else:
                    # Check if the field is a ForeignKey
                    model_field = instance._meta.get_field(field_name)
                    if isinstance(model_field, ForeignKey):
                        # Handle ForeignKey fields
                        related_instance = getattr(instance, field_name, None)
                        if related_instance:
                            if nested_fields:
                                # Use a nested serializer to serialize the FK field with nested fields
                                nested_serializer_class = self.get_nested_serializer(model_field.related_model)
                                nested_serializer = nested_serializer_class(
                                    related_instance,
                                    context={**self.context, 'fields': nested_fields}
                                )
                                representation[field_name] = nested_serializer.data
                            else:
                                # If no nested fields, just return the FK's primary key
                                representation[field_name] = related_instance.pk if type(related_instance) is not int else related_instance
                        else:
                            representation[field_name] = None
                    else:
                        # Handle non-FK fields (e.g., IntegerField, CharField, etc.)
                        model_field = instance._meta.get_field(field_name)

                        # Check for specific field types and process them accordingly
                        if isinstance(model_field, PhoneNumberField):  # Handle PhoneNumberField
                            phone_number = getattr(instance, field_name)
                            representation[field_name] = str(phone_number) if phone_number else None
                        elif isinstance(model_field, DateTimeField):  # Handle DateTimeField
                            datetime_value = getattr(instance, field_name)
                            if datetime_value:
                                # Convert to local time zone
                                local_datetime = localtime(datetime_value)
                                representation[field_name] = local_datetime.strftime('%d-%b-%y | %I:%M:%S %p')
                            else:
                                representation[field_name] = None
                        elif isinstance(model_field, DateField):  # Handle DateField
                            date_value = getattr(instance, field_name)
                            if date_value:
                                # Convert to local time zone (if needed)
                                local_date = date_value.astimezone(get_current_timezone()) if hasattr(date_value, 'astimezone') else date_value
                                representation[field_name] = local_date.strftime('%d-%b-%y')
                            else:
                                representation[field_name] = None
                        elif isinstance(model_field, TimeField):  # Handle TimeField
                            time_value = getattr(instance, field_name)
                            if time_value:
                                # Convert to local time zone (if needed)
                                local_time = time_value.astimezone(get_current_timezone()) if hasattr(time_value, 'astimezone') else time_value
                                representation[field_name] = local_time.strftime('%I:%M:%S %p')
                            else:
                                representation[field_name] = None
                        elif isinstance(model_field, (ImageField, FileField)):  # Handle ImageField and FileField
                            file_field = getattr(instance, field_name)
                            if file_field:
                                # Construct absolute URL
                                base_url = request.build_absolute_uri('/') if request else 'https://api2.securityforce.in/'
                                representation[field_name] = urljoin(base_url, file_field.url)
                            else:
                                representation[field_name] = None
                        else:
                            # Default handling for other field types
                            representation[field_name] = getattr(instance, field_name, None)
            return representation
        except Exception as e:
            print(traceback.format_exc())
            # Log the error for debugging
            print(f"Error in to_representation: {e}")
            return {"error": str(e)}
            