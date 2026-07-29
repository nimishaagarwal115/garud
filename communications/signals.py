from django.db.models.signals import post_save, post_delete
from django.dispatch import Signal, receiver
from django.contrib.contenttypes.models import ContentType
from django.db import connection

# Define the operation_signal
operation_signal = Signal()

@receiver(post_save)
def handle_model_save(sender, instance, created, **kwargs):
    """
    Handles post_save signal for all models.
    Determines whether the action is 'create' or 'update' and triggers the operation_signal.
    """
    # Skip signal during migrations
    if 'django_content_type' not in connection.introspection.table_names():
        return

    # Determine the action
    action = 'create' if created else 'update'

    # Get the model name
    # model_name = ContentType.objects.get_for_model(sender).model    

    
    # print(f"INSTANCE:: {instance}, sender: {sender}, Modified BY: {getattr(instance, 'modified_by', None)}, business: {getattr(instance, 'business', None)} - Action: {action.capitalize()} {model_name.replace('_', ' ')}, INstance: {str(instance)}, ID: {instance.pk}")
    # Trigger the operation_signal
    # operation_signal.send(
    #     sender=sender,
    #     user=getattr(instance, 'modified_by', None),  # Assuming 'modified_by' is set on the instance
    #     current_business=getattr(instance, 'business', None),  # Assuming 'business' is set on the instance
    #     action=f"{action.capitalize()} {model_name.replace('_', ' ')}",
    #     instance=str(instance),  # Convert the instance to a string representation
    #     id=instance.pk,  # Use the instance ID only if created is True
    # )

# @receiver(post_delete)
# def handle_model_delete(sender, instance, **kwargs):
#     """
#     Handles post_delete signal for all models.
#     Triggers the operation_signal with the 'delete' action.
#     """
#     # Get the model name
#     model_name = ContentType.objects.get_for_model(sender).model

#     # Trigger the operation_signal
#     operation_signal.send(
#         sender=sender,
#         user=getattr(instance, 'modified_by', None),  # Assuming 'modified_by' is set on the instance
#         current_business=getattr(instance, 'business', None),  # Assuming 'business' is set on the instance
#         action=f"Delete {model_name.replace('_', ' ')}",
#         instance=str(instance),  # Convert the instance to a string representation
#         id=None,  # ID is not relevant for deleted instances
#     )
