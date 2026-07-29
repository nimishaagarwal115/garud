import requests
from django.conf import settings
from log.models import OTPLog
import random

def generate_otp():
    return str(random.randint(100000, 999999))

def send_sms_otp(mobile_number, purpose="NumberChanged", session=None):
    if not mobile_number:
        return {"success": False, "error": "Mobile number is required"}

    otp = generate_otp()

    params = {
        "authorization": settings.SMS_AUTHORIZATION,
        "route": settings.SMS_ROUTE,
        "sender_id": settings.SMS_SENDER_ID,
        "message": "293",
        "variables_values": otp,
        "flash": "0",
        "numbers": mobile_number,
    }

    try:
        response = requests.get("https://sms.shivaaycreations.in/dev/api", params=params)
        api_response = response.json()

        OTPLog.objects.create(
            otp=otp,
            device=mobile_number,
            device_type='mobile',
            purpose=purpose,
            content=str(api_response),
            status='generated'
        )

        if session:
            session['otp'] = otp

        return {"success": True, "message": "OTP sent successfully via SMS"}

    except requests.RequestException as e:
        return {"success": False, "error": "Failed to send SMS OTP", "details": str(e)}
    
def validate_otp(phone, otp, purpose="Login"):
    latest_otp_entry = OTPLog.objects.filter(device=phone, purpose=purpose).order_by('-created_at').first()
    return latest_otp_entry and latest_otp_entry.otp == otp
