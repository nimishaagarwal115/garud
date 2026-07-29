from celery import shared_task
from .models import ScheduledNotification
from .services import CommunicationService
from django.utils.timezone import now

@shared_task
def process_scheduled_notifications():
    """
    Processes all scheduled notifications that are due to be sent.
    """
    notifications = ScheduledNotification.objects.filter(sent=False, scheduled_time__lte=now())
    for notification in notifications:
        # Get recipients based on the notification type
        if notification.type == 'email':
            recipients = [user.email for user in notification.recipients.all()]
            CommunicationService.send_email(notification.subject, notification.body, recipients)
        elif notification.type == 'sms':
            recipients = [user.phone_number for user in notification.recipients.all() if user.phone_number]
            CommunicationService.send_sms(notification.body, recipients)
        elif notification.type == 'push':
            recipients = [user.expo_push_token for user in notification.recipients.all() if user.expo_push_token]
            CommunicationService.send_push_notification(notification.body, recipients)
        elif notification.type == 'whatsapp':
            recipients = [user.phone_number for user in notification.recipients.all() if user.phone_number]
            CommunicationService.send_whatsapp_message(notification.body, recipients)

        # Mark the notification as sent
        notification.sent = True
        notification.save()