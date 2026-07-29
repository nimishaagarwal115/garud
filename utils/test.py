from django.test import TestCase
from rest_framework import status
from rest_framework.response import Response
from utils.generics import success_response, error_response
from unittest.mock import patch
from utils.otp_handler import isValidMobile, sendMobileOTP, OTPHandler

class GenericsResponseTest(TestCase):

    def test_success_response_default(self):
        # Test success_response with default parameters
        response = success_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            "status": "success",
            "message": "Success",
            "data": "Success"
        })

    def test_success_response_with_custom_message_and_data(self):
        # Test success_response with custom message and data
        response = success_response(message="Operation completed", data={"key": "value"}, status_code=201)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {
            "status": "success",
            "message": "Operation completed",
            "data": {"key": "value"}
        })

    def test_error_response_default(self):
        # Test error_response with default parameters
        response = error_response("An error occurred")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "status": "error",
            "message": "An error occurred",
            "errors": "An error occurred"
        })

    def test_error_response_with_custom_status_code(self):
        # Test error_response with a custom status code
        response = error_response("Unauthorized access--401")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {
            "status": "error",
            "message": "Unauthorized access",
            "errors": "Unauthorized access"
        })

    def test_error_response_with_errors_and_data(self):
        # Test error_response with additional errors and data
        response = error_response("Validation failed", errors="Invalid input", data={"field": "error"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {
            "status": "error",
            "message": "Validation failed",
            "errors": "Invalid input",
            "data": {"field": "error"}
        })

class OTPHandlerTest(TestCase):
    def setUp(self):
        # Set up initial data for testing
        self.valid_mobile = '1234567890'
        self.invalid_mobile = '12345'
        self.otp_type = 'authentication'
        self.otp_value = '1234'

    def test_is_valid_mobile(self):
        # Test valid mobile number
        self.assertTrue(isValidMobile(self.valid_mobile))
        # Test invalid mobile number
        self.assertFalse(isValidMobile(self.invalid_mobile))

    # @patch('utils.otp_handler.send_sms')
    # def test_send_mobile_otp(self, mock_send_sms):
    #     # Test sending OTP to a valid mobile number
    #     response = sendMobileOTP(self.valid_mobile, self.otp_value, self.otp_type)
    #     self.assertEqual(response, "OTP sent successfully.")
    #     mock_send_sms.assert_called_once_with(self.valid_mobile, f"Here is Your OTP: {self.otp_value}")

    #     # Check if OTPLog entry is created
    #     otp_log = OTPLog.objects.filter(mobile=self.valid_mobile, otp_type=self.otp_type, otp_value=self.otp_value)
    #     self.assertTrue(otp_log.exists())

    @patch('utils.otp_handler.sendMobileOTP')
    def test_generate_otp(self, mock_send_mobile_otp):
        # Test generating OTP for a valid mobile number
        response = OTPHandler.generate_otp(self.valid_mobile, self.otp_type)
        self.assertIn('OTP', response)
        mock_send_mobile_otp.assert_called_once()

        # Test generating OTP for an invalid mobile number
        with self.assertRaises(ValueError) as context:
            OTPHandler.generate_otp(self.invalid_mobile, self.otp_type)
        self.assertEqual(str(context.exception), "Invalid mobile number!")

    def test_verify_otp(self):
        # Create an OTPLog entry for testing
        # OTPLog.objects.create(mobile=self.valid_mobile, otp_type=self.otp_type, otp_value=self.otp_value, status='new')

        # Test verifying a valid OTP
        response = OTPHandler.verifyOTP(self.valid_mobile, self.otp_type, self.otp_value)
        self.assertTrue(response)

        # Test verifying an invalid OTP
        with self.assertRaises(ValueError) as context:
            OTPHandler.verifyOTP(self.valid_mobile, self.otp_type, '654321')
        self.assertEqual(str(context.exception), "Invalid Mobile OTP")