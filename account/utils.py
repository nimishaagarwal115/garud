import random
import requests

def generate_otp(length=4):
    return str(random.randint(10**(length-1), 10**length-1))

def send_sms_otp(phone_number, otp):
    url = (
        "https://sms.shivaaycreations.in/dev/api"
        "?authorization=X9LbVpOhQlKM4BuRkS0mr8c1CHZYny3Pw6alIt59WFjUEdzg7AMdprm3K9TCWk7FGlQ684DgsPe2toUw"
        "&route=dlt"
        "&sender_id=PLACTV"
        "&message=293"
        f"&variables_values={otp}"
        "&flash=0"
        f"&numbers={phone_number}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Failed to send OTP SMS: {e}")
        return False