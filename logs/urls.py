from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'otplogs', OTPLogViewSet)
router.register(r'apirequestlogs', APIRequestLogViewSet)

urlpatterns = [
    path('', include(router.urls)),
]