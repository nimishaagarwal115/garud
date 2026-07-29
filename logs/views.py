from rest_framework import viewsets
from .models import *
from .serializers import *

class OTPLogViewSet(viewsets.ModelViewSet):
    queryset = OTPLog.objects.all()
    serializer_class = OTPLogSerializer

class APIRequestLogViewSet(viewsets.ModelViewSet):
    queryset = APIRequestLog.objects.all()
    serializer_class = APIRequestLogSerializer