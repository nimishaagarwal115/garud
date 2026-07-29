from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
# from logs.models import AccessLog
import json

UserModel = get_user_model()

class PINPasswordAuthenticationBackend(ModelBackend):

    def authenticate(self, request, mobile=None, otp=None, **kwargs):
        try:     
            if not request:
                return None
            if not mobile:
                mobile = kwargs.get('mobile')
            if not otp:
                otp = kwargs.get('otp')
                     
            try:
                user = UserModel.objects.get(mobile=mobile)
            except UserModel.DoesNotExist:
                self.log_access(request, None, "Login failed - User does not exist")
                return None
          
            # Check if the otp matches  
            if otp and otp == '1234':
                self.log_access(request, user, "Login successful")
                return user
            else:
                self.log_access(request, None, "Login failed - Incorrect credentials")
                return None

                
        except UserModel.DoesNotExist:
            self.log_access(request, None, "Login failed - User does not exist")
            return None
        except Exception as e:
            self.log_access(request, None, f"Login failed - {str(e)}")
            return None
            
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def log_access(self, request, user, action):
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # AccessLog.objects.create(
        #     user=user,
        #     action=action,
        #     details=json.dumps({k: v for k, v in request.headers.items()}),  # Convert headers to regular dict
        #     ip_address=ip_address,
        #     user_agent=user_agent
        # )
