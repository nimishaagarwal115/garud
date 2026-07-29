from utils.generics import success_response, error_response
from django.utils.timezone import now
from django.utils.crypto import get_random_string
from django.conf import settings
from logs.models import OTPLog
from datetime import timedelta
from typing import Literal
import traceback
import re

# Assuming you have a function to send SMS
def send_sms(mobile, content):
    # Implement SMS sending logic here
    pass

def isValidMobile(mobile):
    if mobile is None:
        return False
    pattern = r'^\d{10,15}$'  # Adjust the regex pattern as needed
    return True if re.match(pattern, mobile) else False

def sendMobileOTP(mobile, otp, otp_type):
    try:
        content = f"Here is Your OTP: {otp}"
        send_sms(mobile, content)  # Use the SMS sending function
        otp_log = OTPLog.objects.create(mobile=mobile, otp_type=otp_type, otp_value=otp)
        otp_log.save()

        return "OTP sent successfully."
    except Exception as e:
        print(str(e), traceback.format_exc())
        raise e

class OTPHandler:
    otp_type_literal = Literal['authentication', 'verification', 'transaction', 'reset', 'confirmation']
    
    @staticmethod
    def generate_otp(mobile, otp_type: otp_type_literal):
        # otp = get_random_string(length=6, allowed_chars='1234567890')
        if isValidMobile(mobile):
            # sendMobileOTP(mobile, otp, otp_type)
            return success_response("success")
        else:
            raise ValueError("Invalid mobile number!")

    @staticmethod
    def verifyOTP(mobile, otp_type: otp_type_literal, otp):
        if otp == '1234':
            return success_response("success")
        else:
            raise ValueError("Invalid OTP")
        # db_otp = OTPLog.objects.filter(mobile=mobile, otp_type=otp_type, otp_value=otp, status='new')
        # if not db_otp.first():
        #     raise ValueError("Invalid Mobile OTP")
        # else:
            threshold_time = now() - timedelta(minutes=2)
            db_otp = db_otp.filter(timestamp__lte=threshold_time)
            if db_otp.first():
                db_otp.update(status='expired')
                raise ValueError("OTP expired!")
            else:
                db_otp.update(status='used', is_validated=True)
                return True 
        