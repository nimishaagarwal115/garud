
from logs.models import OTPLog
from django.core.mail import send_mail
from django.conf import settings
import environ
env = environ.Env()
from communications.services import CommunicationService
from django.template.loader import render_to_string

def sendEmailOTP(email, otp, purpose):
    try:
        subject = 'OTP Verification From Security Force'
        context = {
            "subject": subject,
            "otp": otp,
            "year": settings.YEAR,
            "logo_url": settings.LOGO_URL,
            "static_url": settings.CURRENT_HOST,
        }
        html_body = render_to_string("emails/otp_email.html", context)
        plain_body = f"Here is Your OTP: {otp}"

        CommunicationService.send_email(
            subject=subject,
            body=plain_body,
            recipients=[email],
            html_body=html_body
        )        
        
        otp_log = OTPLog.objects.create(otp=otp, device=email, device_type="email", purpose=purpose, content=plain_body)
        otp_log.save()        
        return "OTP email sent successfully."
    except Exception as e:
        raise e

def sendMobileOTP(mobile, otp, purpose):
    print(f"Sending OTP to mobile11: {mobile}")
    content = f"Here is Your OTP: {otp}"
    otp_log = OTPLog.objects.create(otp=otp, device=mobile, device_type="mobile", purpose=purpose, content=content)
    print(f"Sending OTP to mobile22: {mobile}")
    otp_log.save()
    print(f"otp saved to database: {mobile} {otp_log}")
    CommunicationService.send_sms(otp, [mobile])
    return "OTP mobile sent successfully."

def sendPanOTP(pan, otp, purpose):
    content = f"Here is Your OTP: {otp}"
    otp_log = OTPLog.objects.create(otp=otp, device=pan, device_type="pan", purpose=purpose, content=content)
    otp_log.save()   

def fetch_directions_from_api(route):
    return None