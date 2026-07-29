from django.db.models import *
from django.db import transaction

# Create your models here.
class OTPLog(Model):
    TYPES = [
        ('mobile', 'Mobile'),
        ('email', 'Email'),
        ('pan', 'PAN'),
    ]
    STATUS = [
        ('generated', 'Generated'),
        ('expired', 'Expired'),
        ('verified', 'Verified'),
    ]
    otp = CharField(max_length=6)
    device = CharField(max_length=254)
    device_type = CharField(max_length=20, choices=TYPES, default = "Mobile")
    purpose = CharField(max_length=30, default="Login")
    content = TextField()
    status = CharField(max_length=10, choices=STATUS, default = "generated")
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'OTP Log'
        verbose_name_plural = 'OTP Logs'

    def __str__(self):
        return f"---{self.device} - ({self.otp})"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Expire existing generated OTPs for the same device
            OTPLog.objects.filter(device=self.device, purpose=self.purpose, status='generated').update(status='expired')
            # Save the new OTP
            super().save(*args, **kwargs)

class APIRequestLog(Model):
    api_url = CharField(max_length=255)
    request_data = TextField()
    response_data = TextField()
    datetime = DateTimeField()
    ip_address = CharField(max_length=45)
    response_status = PositiveSmallIntegerField()
    request_method = CharField(max_length=10, default="GET")
    request_user = CharField(max_length=255, default="AnonymousUser")

    def __str__(self):
        return f"{self.api_url} - {self.datetime}"