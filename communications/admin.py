from django.contrib import admin
from .models import NotificationTemplate, NotificationLog, ScheduledNotification

@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "type", "subject", "created_at")
    search_fields = ("name", "type", "subject", "body", "html_body")
    list_filter = ("type", "created_at")

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "recipient", "device",  "subject", "status", "sent_at", "created_at")
    search_fields = ("recipient__mobile", "recipient__email", "recipient__fullname", "subject", "body", "status")
    list_filter = ("type", "status", "created_at", "sent_at")

@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "subject", "scheduled_time", "sent")
    search_fields = ("subject", "body", "recipients__username", "recipients__email")
    list_filter = ("type", "sent", "scheduled_time")


