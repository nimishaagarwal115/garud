from django.test import TestCase
from unittest.mock import patch
from communications.utils import send_sms

class SendSMSTestCase(TestCase):
    @patch("communications.utils.requests.post")
    def test_send_sms(self, mock_post):
        """
        Test the send_sms function with mock requests.
        """
        # Mock response for the SMS API
        mock_post.return_value.status_code = 200
        mock_post.return_value.text = "SMS sent successfully"

        # Test data
        body = "This is a test SMS."
        phone_numbers = ["+919680450598", "+919799992111"]

        # Call the function
        send_sms(body, phone_numbers)
        
        # Assertions
        mock_post.assert_called_once()
        self.assertEqual(mock_post.call_count, 1)  # Ensure the API was called once
        self.assertIn("numbers", mock_post.call_args.kwargs["json"])  # Check payload
        self.assertEqual(
            mock_post.call_args.kwargs["json"]["numbers"],
            ",".join(phone_numbers),
        )
        self.assertEqual(mock_post.return_value.status_code, 200)