from rest_framework import serializers
from utils.serializers import DynamicFieldsModelSerializer
from .models import User
import traceback
from django.db import models


class UserSerializer(DynamicFieldsModelSerializer):   

    class Meta:
        model = User
        fields = [
            'id', 'fullname', 'email', 'mobile', 'photo', 'last_login', 'is_active', 
            'is_email_verified', 'is_mobile_verified', 'expo_push_token',
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop('password', None)  # Remove password from the representation
        data['is_password_set'] = bool(instance.password)  # Check if password is set
        data['is_seller'] = instance.is_seller  # Check if user has government details

        return data
