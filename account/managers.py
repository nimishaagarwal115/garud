from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, fullname=None, email=None, **extra_fields):
        if not mobile:
            raise ValueError("Mobile number must be set.")

        user = self.model(mobile=mobile, fullname=fullname, email=email, **extra_fields)
        
        if password is not None:
            # Validate password using Django's validators
            validate_password(password)
            user.set_password(password)
        else:
            user.password = None
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, fullname=None, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(mobile, password, fullname, email, **extra_fields)