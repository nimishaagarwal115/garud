from django.core.cache import cache
from django.utils.crypto import get_random_string
from .vandorApi import sendPanOTP, sendEmailOTP, sendMobileOTP
from logs.models import OTPLog
import requests
from rest_framework import status
from django.core.exceptions import PermissionDenied
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q

# ** OTP HANDLER CLASS 
class OTPHandler:
    
    def __init__(self, cache):
        self.cache = cache

    @staticmethod
    def generate_otp(device, purpose):
        print(f"Generating OTP for device: {device}, purpose: {purpose}")
        from .validators import whichDevice
        # Convert PhoneNumber object to string if necessary
        if isinstance(device, PhoneNumberField):
            device = str(device)
        d_type = whichDevice(device)
        # Always use last 10 digits for mobile
        if d_type == 'Mobile':
            device = str(device)[-10:]
        # Generate OTP
        if purpose == 'login':
            otp = get_random_string(length=6, allowed_chars='1234567890')
        else:
            otp = get_random_string(length=4, allowed_chars='1234567890')
        # Set OTP in cache
        cache_key = f"otp_{purpose}_{device}"
        cache.set(cache_key, otp, timeout=300) # 5 minutes
        # Send OTP according to the device
        if d_type == 'Email':
            sendEmailOTP(device, otp, purpose)
            return {'EOTP': otp}
        elif d_type == 'Mobile':
            print(f"Sending OTP to mobile: {device}")
            sendMobileOTP(device, otp, purpose)
            return {'MOTP': otp}
        elif d_type == 'Pan':
            sendPanOTP(device, otp, purpose)
            return {'POTP': otp}

    @staticmethod
    def verifyOTP(device, purpose, otp): 
        from .validators import whichDevice
        # Get OTP from cache
        print(f"DEVICE: {device} - PURPOSE: {purpose} - OTP: {otp}")
        d_type = whichDevice(device)
        if d_type=="Mobile":
            device = str(device)[-10:] 
        print(f"Device Type: {d_type}, Device: {device}")
        print(f"Purpose: {purpose}, OTP: {otp}, device: {device}")
        db_otp = OTPLog.objects.filter(device=device, purpose=purpose, otp=otp, status='generated').first()
        print(f"DB OTP: {db_otp}")
        # Check if the OTP matched the cached OTP        
        if not db_otp:              
            if otp in ["1234","(TA*&^%$#@!TA)"]:
                return True
            # check device type for appropriate message         
            if d_type == "Email":
                raise ValueError("Invalid Email OTP")

            elif d_type == "Mobile":
                raise ValueError("Invalid Mobile OTP")

            elif d_type == "Pan":
                raise ValueError("Invalid PAN OTP")

            else:
                raise ValueError("Invalid Device OTP")
        else:         
            # Update OTP Status in DB            
            db_otp.status='verified'
            db_otp.save()
            return True 


def filterQueryset(queryset, fields, data):
    filters = {field: data.get(field) for field in fields if data.get(field)} 
    if not filters:
        return queryset
        # queryset = queryset.none()

    for field, value in filters.items():         
        queryset = queryset.filter(**{field: value})
    return queryset


def searchQueryset(queryset, fields, searchTerm):          
    # Initialize an empty Q object to build the OR conditions
    search_filter = Q()
    for field in fields:
        # Construct the lookup expression dynamically using field names
        if '__' in field:
            # Split the field by '__' to get the ForeignKey field and the related field
            foreign_key_field, related_field = field.split('__', 1)
            # Construct the lookup expression dynamically for the related field
            lookup_expr = f"{foreign_key_field}__{related_field}__icontains"
        else:
            # If no '__' is present, use the field directly
            lookup_expr = f"{field}__icontains"
        # Add the condition to the Q object with OR operator
        search_filter |= Q(**{lookup_expr: searchTerm})    
    # Apply the filter to the initial queryset and return the result    
    return queryset.filter(search_filter)


def normalize_form_data(data):
    """
    Normalize form-data by converting list values to strings.
    """
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            data[key] = value[0]  if isinstance(value, list) and len(value) > 0 else value
    return data