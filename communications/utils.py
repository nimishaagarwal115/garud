from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import requests
from django.template.loader import render_to_string

def send_email(subject, plain_body, recipient_list, html_body=None, context=None, sender_name="SecurityForce for Business"):
    """
    Sends an email with a base HTML template and plain text fallback.
    """
    # Render the base HTML template with the provided context
    if html_body is None:
        html_body = render_to_string("emails/base_email.html", context or {})

    # Format the sender name and email
    from_email = f"{sender_name} <{settings.DEFAULT_FROM_EMAIL}>"

    # Create the email object
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_body,  # Plain text fallback
        from_email=from_email,
        to=recipient_list,
    )
    # Attach the HTML version
    email.attach_alternative(html_body, "text/html")
    email.send()

def send_sms(body, phone_numbers):
    """
    Sends SMS using the SMS API defined in base.py.
    """
    print(f"Sending SMS to final: {phone_numbers}")
    url = settings.SMS_API_URL
    headers = {
        "Authorization": settings.SMS_AUTHORIZATION,
        "Content-Type": "application/json",
    }
    payload = {
        "route": settings.SMS_ROUTE,
        "sender_id": settings.SMS_SENDER_ID,
        "message": "293",
        "variables_values": body, # Assuming body is a string with variables to replace like {otp}
        "numbers": ",".join(phone_numbers),
    }
    
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        print("SMS sent successfully")
    else:
        print(f"Failed to send SMS: {response.status_code} - {response.text}")

def send_push_notification(body, device_tokens):
    """
    Sends push notifications using the Expo Push Notification API.
    """
    # Expo push notification endpoint
    url = "https://exp.host/--/api/v2/push/send"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Validate screen and id
    if not screen:
        raise ValueError("Screen identifier is required for push notifications.")
    link = f"securityforce://{screen}/{id}" if id else f"securityforce://{screen}"

    payload = {
        "to": expo_token,
        "title": title,
        "body": body,
        "data": {
            "icon": "https://api2.securityforce.in/static/dashboard/img/favicon/favicon.png",
            "link": link,
        },
    }

    response = requests.post(url, data=json.dumps(payload), headers=headers)
    
    if response.status_code == 200:
        print("Notification sent successfully")
    else:
        print(f"Failed to send notification: {response.status_code} - {response.text}")

def send_whatsapp_message(body, phone_numbers):
    """
    Sends WhatsApp messages using Twilio API.
    """
    TWILIO_ACCOUNT_SID = settings.TWILIO_ACCOUNT_SID
    TWILIO_AUTH_TOKEN = settings.TWILIO_AUTH_TOKEN
    TWILIO_WHATSAPP_NUMBER = settings.TWILIO_WHATSAPP_NUMBER

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
    for phone in phone_numbers:
        payload = {
            "From": f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            "To": f"whatsapp:{phone}",
            "Body": body,
        }
        response = requests.post(url, data=payload, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN))
        if response.status_code == 201:
            print("WhatsApp message sent successfully")
        else:
            print(f"Failed to send WhatsApp message: {response.status_code} - {response.text}")

def create_seller_notification(seller, title, message, category='PRODUCT_ADDED', image=None):
    from .models import SellerNotification
    return SellerNotification.objects.create(
        seller=seller,
        title=title,
        message=message,
        category=category,
        image=image
    )

def create_customer_notification(user, title, message, category='SYSTEM', image=None, target_url=None):
    from .models import CustomerNotification, CustomerNotificationPreference
    # Check preference
    pref, created = CustomerNotificationPreference.objects.get_or_create(user=user)
    if not pref.is_enabled:
        return None
        
    return CustomerNotification.objects.create(
        user=user,
        title=title,
        message=message,
        category=category,
        image=image,
        target_url=target_url
    )