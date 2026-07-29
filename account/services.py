from utils.services import BaseService
from .serializers import UserSerializer
from django.contrib.auth import get_user_model
from django.db import transaction
from utils.functions import OTPHandler

User = get_user_model()

class UserService:
    model = User
    serializer_class = UserSerializer

    @classmethod
    def get(cls, pk, request=None, business_field=None):
        return User.objects.get(pk=pk)

    @classmethod
    def get_all(cls, request=None, filters=None):
        queryset = User.objects.all()
        if filters:
            queryset = queryset.filter(**filters)
        return queryset

    @classmethod
    @transaction.atomic
    def create(cls, data, request=None):
        mobile_otp = data.pop('mobile_otp', None)
        email_otp = data.pop('email_otp', None)
        mobile = data.get('mobile')
        email = data.get('email')

        serializer = cls.serializer_class(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Mobile verification
        if mobile and mobile_otp:
            try:
                OTPHandler.verifyOTP(mobile, 'registration', mobile_otp)
                user.is_mobile_verified = True
            except Exception:
                user.is_mobile_verified = False
        else:
            user.is_mobile_verified = False

        # Email verification
        if email and email_otp:
            try:
                OTPHandler.verifyOTP(email, 'registration', email_otp)
                user.is_email_verified = True
            except Exception:
                user.is_email_verified = False
        else:
            user.is_email_verified = False

        user.save()
        return user

    @classmethod
    @transaction.atomic
    def update(cls, pk, data, request=None, business_field=None):
        user = cls.get(pk)
        old_mobile = user.mobile
        old_email = user.email

        mobile_otp = data.pop('mobile_otp', None)
        email_otp = data.pop('email_otp', None)
        new_mobile = data.get('mobile', old_mobile)
        new_email = data.get('email', old_email)

        serializer = cls.serializer_class(user, data=data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Mobile verification logic
        if 'mobile' in data and new_mobile != old_mobile:
            if mobile_otp:
                try:
                    OTPHandler.verifyOTP(new_mobile, 'verify_mobile', mobile_otp)
                    user.is_mobile_verified = True
                except Exception:
                    user.is_mobile_verified = False
            else:
                user.is_mobile_verified = False

        # Email verification logic
        if 'email' in data and new_email != old_email:
            if email_otp:
                try:
                    OTPHandler.verifyOTP(new_email, 'verify_email', email_otp)
                    user.is_email_verified = True
                except Exception:
                    user.is_email_verified = False
            else:
                user.is_email_verified = False

        user.save()
        return user

    @classmethod
    @transaction.atomic
    def delete(cls, pk, request=None, business_field=None):
        user = cls.get(pk)
        user.delete()
        return {"message": "User deleted successfully."}

    @classmethod
    @transaction.atomic
    def deactivate(cls, pk, request=None):
        user = cls.get(pk)
        user.is_active = False
        user.save()
        return user
    
    @classmethod
    @transaction.atomic
    def reactivate(cls, pk, request=None):
        user = cls.get(pk)
        user.is_active = True
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def update_photo(cls, pk, photo, request=None):
        user = cls.get(pk)
        user.photo = photo
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def set_mobile_verified(cls, pk, status=True):
        user = cls.get(pk)
        user.is_mobile_verified = status
        user.save()
        return user

    @classmethod
    @transaction.atomic
    def set_email_verified(cls, pk, status=True):
        user = cls.get(pk)
        user.is_email_verified = status
        user.save()
        return user
