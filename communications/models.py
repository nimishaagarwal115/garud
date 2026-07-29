from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class NotificationTemplate(models.Model):
    """
    Stores reusable templates for notifications.
    """
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
        ('push', 'Push Notification'),
        ('websocket', 'WebSocket'),
    ]
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)  # For email
    body = models.TextField()  # For plain text content
    html_body = models.TextField(blank=True, null=True)  # For HTML content
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} ({self.type})"


class NotificationLog(models.Model):
    """
    Logs all notifications sent for tracking and debugging.
    """
    TYPE_CHOICES = NotificationTemplate.TYPE_CHOICES
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    device = models.CharField(max_length=255)  # Email, phone number, or user ID
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications_logs", null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    status = models.CharField(max_length=50, default="Pending")  # Pending, Sent, Failed
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.type} to {self.recipient} ({self.status})"


class ScheduledNotification(models.Model):
    """
    Stores notifications to be sent at a scheduled time.
    """
    TYPE_CHOICES = NotificationTemplate.TYPE_CHOICES
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()
    recipients = models.ManyToManyField(User, related_name="scheduled_notifications")
    scheduled_time = models.DateTimeField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Scheduled {self.type} at {self.scheduled_time}"


class SellerNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('PRODUCT_ADDED', 'Product Added'),
        ('NEW_ORDER', 'New Order'),
        ('PRODUCT_UPDATED', 'Product Updated'),
        ('PRODUCT_DELETED', 'Product Deleted'),
        ('AI_GENERATION_COMPLETED', 'AI Generation Completed'),
        ('AI_GENERATION_FAILED', 'AI Generation Failed'),
        ('PROFILE_UPDATED', 'Profile Updated'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.ImageField(upload_to='notifications/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='PRODUCT_ADDED')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.seller.username}"

class CustomerNotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    is_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {'Enabled' if self.is_enabled else 'Disabled'}"

class CustomerNotification(models.Model):
    NOTIFICATION_TYPES = [
        ('ORDER_UPDATE', 'Order Update'),
        ('OFFER', 'Offer'),
        ('WISHLIST', 'Wishlist'),
        ('PRODUCT', 'Product'),
        ('SYSTEM', 'System'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="customer_notifications")
    title = models.CharField(max_length=255)
    message = models.TextField()
    image = models.ImageField(upload_to='notifications/customer/', null=True, blank=True)
    category = models.CharField(max_length=50, choices=NOTIFICATION_TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    target_url = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.mobile}"
