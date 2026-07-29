from django.db import models, transaction
from core.base.models import BaseModel
from django.utils import timezone

# OTP Log for phone login (PAN, etc. extensible)
class OTPLog(BaseModel):
    TYPE_CHOICES = [
        ('mobile', 'Mobile'),
        ('pan', 'PAN'),
    ]

    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('expired', 'Expired'),
        ('verified', 'Verified'),
    ]

    otp = models.CharField(max_length=6)
    device = models.CharField(max_length=254)
    device_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='mobile')
    purpose = models.CharField(max_length=30,)
    content = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='generated')

    class Meta:
        verbose_name = 'OTP Log'
        verbose_name_plural = 'OTP Logs'

    def __str__(self):
        return f"{self.device} - ({self.otp})"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Expire previously generated OTPs for same device and purpose
            OTPLog.objects.filter(
                device=self.device,
                purpose=self.purpose,
                status='generated'
            ).update(status='expired')
            super().save(*args, **kwargs)


# API Request Log for Debugging / Monitoring
class APIRequestLog(BaseModel):
    api_url = models.CharField(max_length=255)
    request_data = models.TextField()
    response_data = models.TextField()
    datetime = models.DateTimeField()
    ip_address = models.CharField(max_length=45)
    response_status = models.PositiveSmallIntegerField()
    request_method = models.CharField(max_length=10, default="GET")
    request_user = models.CharField(max_length=255, default="AnonymousUser")

    def __str__(self):
        return f"{self.api_url} - {self.datetime}"
