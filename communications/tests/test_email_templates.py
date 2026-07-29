from django.test import TestCase
from django.core import mail
from django.template.loader import render_to_string
from django.conf import settings
from communications.utils import send_email

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
        self.assertEqual(len(mail.outbox), 1)  # Ensure one email is sent
        self.assertEqual(mail.outbox[0].subject, "Welcome to SecurityForce")
        self.assertIn(self.recipient, mail.outbox[0].to)
        self.assertIn("Welcome to SecurityForce", mail.outbox[0].body)  # Plain text
        self.assertIn("Welcome to SecurityForce", mail.outbox[0].alternatives[0][0])  # HTML content

    def test_password_reset_email(self):
        """
        Test the password reset email template.
        """
        context = {
            "subject": "Reset Your Password",
            "body": "You requested a password reset. Click the link below to reset your password.",
            "reset_link": f"{settings.CURRENT_HOST}/reset-password/token",
            "year": self.year,
            "logo_url": self.logo_url,
        }
        html_body = render_to_string("emails/password_reset_email.html", context)
        plain_body = "You requested a password reset. Click the link below to reset your password."

        send_email(
            subject="Reset Your Password",
            plain_body=plain_body,
            recipient_list=[self.recipient],
            html_body=html_body,
        )

        # Assertions
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Reset Your Password")
        self.assertIn(self.recipient, mail.outbox[0].to)
        self.assertIn("You requested a password reset", mail.outbox[0].body)  # Plain text
        # self.assertIn("https://securityforce.in/reset-password/token", mail.outbox[0].alternatives[0][0])  # HTML content

    def test_notification_email(self):
        """
        Test the notification email template.
        """
        context = {
            "subject": "New Notification",
            "body": "You have a new notification in your account.",
            "year": self.year,
            "logo_url": self.logo_url,
        }
        html_body = render_to_string("emails/notification_email.html", context)
        plain_body = "You have a new notification in your account."

        send_email(
            subject="New Notification",
            plain_body=plain_body,
            recipient_list=[self.recipient],
            html_body=html_body,
        )

        # Assertions
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "New Notification")
        self.assertIn(self.recipient, mail.outbox[0].to)
        self.assertIn("You have a new notification", mail.outbox[0].body)  # Plain text
        self.assertIn("You have a new notification", mail.outbox[0].alternatives[0][0])  # HTML content

    def test_account_deactivation_email(self):
        """
        Test the account deactivation email template.
        """
        context = {
            "subject": "Account Deactivated",
            "body": "Your account has been deactivated. Please contact support if this is a mistake.",
            "year": self.year,
            "logo_url": self.logo_url,
        }
        html_body = render_to_string("emails/account_deactivation_email.html", context)
        plain_body = "Your account has been deactivated. Please contact support if this is a mistake."

        send_email(
            subject="Account Deactivated",
            plain_body=plain_body,
            recipient_list=[self.recipient],
            html_body=html_body,
        )

        # Assertions
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Account Deactivated")
        self.assertIn(self.recipient, mail.outbox[0].to)
        self.assertIn("Your account has been deactivated", mail.outbox[0].body)  # Plain text
        self.assertIn("Your account has been deactivated", mail.outbox[0].alternatives[0][0])  # HTML content

    def test_invoice_email(self):
        """
        Test the invoice email template.
        """
        context = {
            "subject": "Your Invoice",
            "body": "Thank you for your payment. Attached is your invoice.",
            "invoice_number": "INV-12345",
            "amount": "$100.00",
            "year": self.year,
            "logo_url": self.logo_url,
        }
        html_body = render_to_string("emails/invoice_email.html", context)
        plain_body = "Thank you for your payment. Attached is your invoice."

        send_email(
            subject="Your Invoice",
            plain_body=plain_body,
            recipient_list=[self.recipient],
            html_body=html_body,
        )

        # Assertions
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Your Invoice")
        self.assertIn(self.recipient, mail.outbox[0].to)
        self.assertIn("Thank you for your payment", mail.outbox[0].body)  # Plain text
        self.assertIn("Thank you for your payment", mail.outbox[0].alternatives[0][0])  # HTML content