from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(OTPLog)
class OTPLogAdmin(admin.ModelAdmin):
    list_display = ('device', 'device_type', 'purpose', 'created_at','updated_at', 'status')
    search_fields = ('device',)
    list_filter = ('device_type', 'purpose', 'status',)

@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = ('api_url', 'request_user', 'ip_address', 'request_method', 'response_status', 'datetime' )
    search_fields = ('api_url','ip_address')
    list_filter = ('response_status', 'request_method')

# admin.site.register(OTPLog)