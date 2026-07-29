from django.db import models

# The `BaseModel` class is an abstract model with `created_at` and `updated_at` with auto_now_add and auto_now set to True fields.
# It will be used to track the creation and last update timestamps of the model instances that inherit from it.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    create_by = models.CharField(max_length=100, null=True, blank=True)
    update_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        abstract = True
