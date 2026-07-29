from .utils import send_email, send_sms, send_push_notification, send_whatsapp_message
from .models import NotificationLog
# from channels.layers import get_channel_layer  # Removed unused import
from asgiref.sync import async_to_sync
import requests

class CommunicationService:
    """
    Centralized service for handling all communication types.
    """

    @staticmethod
    def send_email(subject, body, recipients, html_body=None):
        send_email(subject, body, recipients, html_body)
        for recipient in recipients:
            NotificationLog.objects.create(
                type="email",
                device=recipient,
                # recipient=recipient,
                subject=subject,
                body=body,
                status="Sent",
            )

    @staticmethod
    def send_sms(body, phone_numbers):
        print(f"Sending SMS to: {phone_numbers}")
        send_sms(body, phone_numbers)
        for phone in phone_numbers:
            NotificationLog.objects.create(
                type="sms",
                device=phone,
                # recipient=phone,
                body=body,
                status="Sent",
            )            

    @staticmethod
    def send_push_notification(payload, device_tokens):
        """
        Sends push notifications using the Expo Push Notification API.
        The payload should include the message and optional metadata like screen identifiers.
        """
        message = payload.get("message", "")
        screen = payload.get("screen", None)

        # Send push notifications
        send_push_notification(message, device_tokens, screen)

        # Log the notification
        for token in device_tokens:
            NotificationLog.objects.create(
                type="push",
                device=token,
                # recipient=token,
                body=message,
                status="Sent",
                metadata={"screen": screen} if screen else None,
            )

    @staticmethod
    def send_whatsapp_message(body, phone_numbers):
        send_whatsapp_message(body, phone_numbers)
        for phone in phone_numbers:
            NotificationLog.objects.create(
                type="whatsapp",
                device=phone,
                # recipient=phone,
                body=body,
                status="Sent",
            )