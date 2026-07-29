import re
from django.contrib.auth import get_user_model
from django.db.models import Q
from phonenumber_field.modelfields import PhoneNumberField
import uuid

def isValidPanCardNo(panCardNo):     
    if(panCardNo == None):
        return False    
    pattern = "^[a-zA-Z0-9]+$" 
    pattern1 = "[A-Z]{5}[0-9]{4}[A-Z]{1}"         
    return True if(re.search(pattern,panCardNo) and re.search(pattern1, panCardNo) and len(panCardNo) == 10) else False        

def isValidMobile(mobile):
    """
    Validates if the input is a valid mobile number.
    """
    if not isinstance(mobile, str):
        return False
    
    pattern = r'^\+?[1-9]\d{1,14}$'  # E.164 format
    # pattern = r'^\d{10}$'
    if(mobile == None):
        return False
    # return True if (re.search(pattern, mobile) and len(mobile) == 10) else False
    return True if re.search(pattern, mobile) else False

def isValidEmail(email):
    """
    Validates if the input is a valid email address.
    """
    if not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return True if re.search(pattern, email) else False      

def whichDevice(device):
    # Convert PhoneNumber object to string if necessary
    if isinstance(device, PhoneNumberField):
        device = str(device)
    print(f"Device: {device}")
    try:
        if isValidEmail(device):
            return 'Email'        
        elif isValidMobile(device):
            return 'Mobile'
        elif isValidPanCardNo(device):
            return 'Pan'
        else:
            raise ValueError("OTP device not recognized.")
    except ValueError as e:
        raise e

def isUserRegistered(username):
    User = get_user_model()
    try:
        user = User.objects.get(Q(mobile=username) | Q(email=username))
        return user
    except User.DoesNotExist:
        raise  ValueError("No user exists with this email/mobile")

def is_valid_uuid(uuid_str):
    try:
        uuid_obj = uuid.UUID(uuid_str)
        if not uuid_obj:
            return False
        return True
    except ValueError:
        return False
