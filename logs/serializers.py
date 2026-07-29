from rest_framework import serializers
from .models import *

class OTPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPLog
        fields = '__all__'

class APIRequestLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = '__all__'