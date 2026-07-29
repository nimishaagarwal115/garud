from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from communications.models import NotificationLog

import random

class Command(BaseCommand):
    help = 'Generate 10 sample NotificationLog entries for every user'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        types = ['email', 'sms', 'whatsapp', 'push', 'websocket']
        statuses = ["Pending", "Sent", "Failed"]

        users = User.objects.all()
        count = 0
        for user in users:
            for i in range(10):
                NotificationLog.objects.create(
                    type=random.choice(types),
                    device=f"{user.mobile or user.email or user.id}@example.com",
                    recipient=user,
                    subject=f"Sample Subject {i+1} for {user}",
                    body=f"This is sample notification {i+1} for user {user}.",
                    status=random.choice(statuses),
                    sent_at=timezone.now(),
                    created_at=timezone.now()
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {count} NotificationLog entries for {users.count()} users."))