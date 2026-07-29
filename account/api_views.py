from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import viewsets
from utils.baseModel import Pagination
from utils.generics import success_response, error_response
from utils.viewsets import BaseViewSet
from .serializers import UserSerializer
from rest_framework import filters
import traceback
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from utils.functions import OTPHandler
from logs.models import OTPLog
from .services import UserService
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from utils.drf_response import success_response, error_response
from django.utils import timezone

User = get_user_model()

class GetOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        device = request.data.get('device')
        purpose = request.data.get('purpose', 'login')
        if purpose not in ['login', 'registration', 'verify_mobile', 'verify_email', 'delete_account']:
            return Response({'error': 'Invalid purpose.'}, status=400)
        elif purpose == 'verify_mobile':
            if User.objects.filter(mobile=device if device.startswith("+91") else f"+91{device}").exists():
                if User.objects.get(mobile=device if device.startswith("+91") else f"+91{device}").is_mobile_verified:
                    return Response({'error': 'Mobile number already verified.'}, status=400)
        elif purpose == 'verify_email':
            if User.objects.filter(email=device).exists():
                if User.objects.get(email=device).is_email_verified:
                    return Response({'error': 'Email already verified.'}, status=400)
        elif purpose == 'registration' and User.objects.filter(mobile=device if device.startswith("+91") else f"+91{device}").exists():           
            return Response({'error': 'Mobile number already registered.'}, status=400)
        elif purpose == 'login' and not User.objects.filter(mobile=device if device.startswith("+91") else f"+91{device}").exists():
            return Response({'error': 'Mobile number not registered.'}, status=400)
        # Generate OTP
        if not device:
            return Response({'error': 'Device is required.'}, status=400)
        OTPHandler.generate_otp(device, purpose)
        return Response({'message': 'OTP sent successfully.'})

class CheckRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        mobile = request.data.get('mobile')
        if not mobile:
            return Response({'error': 'Mobile is required.'}, status=400)
        try:
            user = User.objects.get(mobile=mobile)
            has_password = user.password is not None and user.password != ""  and user.has_usable_password()
            return Response({'registered': True, 'password_set': has_password})
        except User.DoesNotExist:
            return Response({'registered': False, 'password_set': False})

class LoginOrRegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import traceback
        try:
            mobile = request.data.get('mobile')
            otp = request.data.get('otp')
            mpin = request.data.get('mpin')
            if not mobile:
                return Response({'error': 'Mobile is required.'}, status=400)
            try:
                mobile = mobile if mobile.startswith("+91") else f"+91{mobile}"
                user = User.objects.get(mobile=mobile)
                # If user is deactivated, only allow OTP login
                if not user.is_active:
                    if not otp:
                        return Response({'error': 'Account is deactivated. Login with OTP only.'}, status=400)
                    try:
                        OTPHandler.verifyOTP(mobile, 'login', otp)
                        user.is_active = True
                        user.save()
                    except Exception as e:
                        return Response({'error': str(e)}, status=400)
                else:
                    # Normal login flow
                    if mpin:
                        if not user.check_password(mpin):
                            return Response({'error': 'Invalid MPIN.'}, status=400)
                    elif otp:
                        try:
                            OTPHandler.verifyOTP(mobile, 'login', otp)
                        except Exception as e:
                            return Response({'error': str(e)}, status=400)
                    else:
                        return Response({'error': 'OTP or MPIN required.'}, status=400)
            except User.DoesNotExist:
                # Register user
                if not otp:
                    return Response({'error': 'OTP required for registration.'}, status=400)
                try:
                    OTPHandler.verifyOTP(mobile, 'registration', otp)
                except Exception as e:
                    return Response({'error': str(e)}, status=400)
                user = User.objects.create_user(mobile=mobile)
            # After successful authentication or registration
            
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        except Exception:
            print(traceback.format_exc())
            return Response({'error': 'Internal server error.'}, status=500)

class SetResetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        new_password = request.data.get('new_password')        
        if not new_password:
            return Response({'error': 'New password and OTP are required.'}, status=400)       
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password set successfully.'})


class UserViewSet(BaseViewSet):
    queryset = User.objects.all()
    serializer_class = UserService.serializer_class
    service_class = UserService
    permission_classes = [IsAuthenticated]    
    filterset_fields = [
        'id',
        'fullname',
        'email',
        'mobile'
    ]
    search_fields = [
        'fullname',
        'email',
        'mobile'
    ]

    @action(detail=True, methods=['post'])
    def set_mobile_verified(self, request, pk=None):
        user = self.get_object()
        mobile = request.data.get('mobile')
        otp = request.data.get('otp')
        if not mobile or not otp:
            return error_response(errors="Mobile and OTP required.", message="Missing data.")
        try:
            OTPHandler.verifyOTP(mobile, 'verify_mobile', otp)
            if(user.mobile != mobile):
                user.mobile = mobile
            user.is_mobile_verified = True
            user.save()
            serializer = self.get_serializer(user)
            return success_response(serializer.data, message="Mobile marked as verified.")
        except Exception as e:
            return error_response(errors=str(e), message="Invalid OTP. or Mobile already registered.")

    @action(detail=True, methods=['post'])
    def set_email_verified(self, request, pk=None):
        user = self.get_object()
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not email or not otp:
            return error_response(errors="Email and OTP required.", message="Missing data.")
        try:
            OTPHandler.verifyOTP(email, 'verify_email', otp)
            user.is_email_verified = True
            user.save()
            serializer = self.get_serializer(user)
            return success_response(serializer.data, message="Email marked as verified.")
        except Exception as e:
            return error_response(errors=str(e), message="Invalid OTP.")

    @action(detail=True, methods=['post'])
    def update_photo(self, request, pk=None):
        user = self.get_object()
        photo = request.FILES.get('photo')
        if not photo:
            return error_response(errors="Photo file required.", message="No photo uploaded.")
        self.service_class.update_photo(pk, photo, request)
        serializer = self.get_serializer(user)
        return success_response(serializer.data, message="Photo updated successfully.")

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.service_class.deactivate(pk, request)
        serializer = self.get_serializer(user)
        return success_response(serializer.data, message="User deactivated successfully.")
    
    @action(detail=True, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def reactivate(self, request, pk=None):
        user = self.service_class.reactivate(pk, request)
        serializer = self.get_serializer(user)
        return success_response(serializer.data, message="User reactivated successfully.")

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # If using DRF TokenAuthentication
        Token.objects.filter(user=request.user).delete()
        # Optionally, also log out the user from the session
        from django.contrib.auth import logout
        logout(request)
        return Response({"success": True, "message": "Logged out successfully."}, status=status.HTTP_200_OK)

class DeleteAccountAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = request.data.get('otp')
        
        if not otp:
            return Response({'error': 'OTP is required.'}, status=400)
            
        try:
            mobile = str(user.mobile)
            OTPHandler.verifyOTP(mobile, 'delete_account', otp)
            
            # Hard delete the account and all cascading data
            user.delete()
            
            # Logout session
            from django.contrib.auth import logout
            logout(request)
            
            return Response({'message': 'Account deleted successfully.'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
