from django.test import TestCase, override_settings
from django.core import mail
from django.template.loader import render_to_string
from django.conf import settings
from communications.utils import send_email

@override_settings(EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend')
class EmailTemplateTests(TestCase):
    def setUp(self):
        self.recipient = "piyush@technoace.in"
        self.logo_url = f"{settings.CURRENT_HOST}/static/logo/logo_black_transparent.png"
        self.year = 2025

    def test_welcome_email(self):
        """
        Test the welcome email template.
        """
        context = {
            "subject": "Welcome to SecurityForce",
            "body": "Welcome to SecurityForce! We're excited to have you on board.",
            "year": self.year,
            "logo_url": self.logo_url,
            "static_url": settings.CURRENT_HOST,
            "recipient_email": self.recipient,
        }
        html_body = render_to_string("emails/welcome_email.html", context)
        plain_body = "Welcome to SecurityForce! We're excited to have you on board."

        send_email(
            subject="Welcome to SecurityForce",
            plain_body=plain_body,
            recipient_list=[self.recipient],
            html_body=html_body,
        )

        # Assertions
        self.assertEqual(len(mail.outbox), 0)  # Emails won't be in the outbox when using SMTP