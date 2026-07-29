from django.contrib import admin
from log.models import OTPLog, APIRequestLog

# Register your models here.
admin.site.register(OTPLog)
admin.site.register(APIRequestLog)