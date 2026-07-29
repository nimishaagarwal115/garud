import uuid
from django.db.models import *
from account.managers import UserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator, MinLengthValidator
from datetime import date
from core.base.models import BaseModel
from django.utils.text import slugify
from core.base.models import BaseModel
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings
from django.conf import settings


# Custom Validations

# TODO: Validation using regex logic review for PHONE_NUMBER_REGEX, AADHAR_REGEX, PAN_REGEX, GST_REGEX
# Phone number validation — digits only
PHONE_NUMBER_REGEX = RegexValidator(r"^[0-9]*$", "Only valid phone number is required")

# Aadhar number validator: 12 digits
AADHAR_REGEX = RegexValidator(r"^\d{12}$", "Aadhar number must be exactly 12 digits.")

# PAN number validator: 5 letters, 4 digits, 1 letter
PAN_REGEX = RegexValidator(r"^[A-Z]{5}[0-9]{4}[A-Z]$", "Invalid PAN format.")

# GST number validator: 15 characters total (simplified check)
GST_REGEX = RegexValidator(r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$", "Invalid GST number.")

# Create your models here.

# Role model to define different user roles.
class RoleModel(Model):
    name = CharField(max_length=50, unique=True) # Role name should be unique

    def __str__(self):
        return self.name

# Language preference model to store supported languages
class LanguagePreferenceModel(Model):
    name = CharField(max_length=50, unique=True) # Example: Hindi, English
    code = CharField(max_length=10, unique=True) # Example: 'en-US', 'hi-IN'

    def __str__(self):
        return self.name

# ===================================== Custom User Model =====================================
# Custom user model extending Django's AbstractBaseUser and PermissionsMixin for auth capabilities
class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    fullname = CharField(max_length=100, null=True, blank=True)
    email = EmailField(max_length=254, db_index=True, blank=True, null=True)
    mobile = PhoneNumberField(region='IN', unique=True, db_index=True)
    photo = ImageField(blank=True, null=True, upload_to="users/photos/")
    address = TextField(('address'), null=True, blank=True)
    registration_datetime = DateTimeField(auto_now_add=True, null=True, blank=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    is_email_verified = BooleanField(default=False)
    is_mobile_verified = BooleanField(default=False)
    expo_push_token = CharField(max_length=255, blank=True, null=True)
    password = CharField(max_length=128, blank=True, null=True)
    # Primary identifier: phone number   
    
    # Role and language preference are nullable and optional
    roles = ForeignKey(
        RoleModel,
        on_delete=SET_NULL,
        null=True,
        blank=True
    )
    
    language_preference = ForeignKey(
        LanguagePreferenceModel,
        on_delete=SET_NULL,
        null=True,
        blank=True
    )
    
    # User status flags
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    
    # Custom manager
    objects = UserManager()
    
    # Set phone number as unique username
    USERNAME_FIELD = 'mobile'
    
    def __str__(self):
        return str(self.mobile)

    @property
    def is_seller(self):
        """Check if the user has a seller role."""
        return hasattr(self, 'government_details') and bool(self.government_details)
    
    # Check if user has a specific role
    def has_role(self, role_name):
        return self.roles.name == role_name if self.roles else False

    # Overriding save to auto-assign default role and language preference if not set
    def save(self, *args, **kwargs):
        if self.roles is None:
            role, created = RoleModel.objects.get_or_create(name='Customer')
            if created:
                role.save()
            self.roles = role

        if self.language_preference is None:
            lang, created = LanguagePreferenceModel.objects.get_or_create(name='Hindi', code='hi-IN') # TODO: make it hi ONLY
            if created:
                lang.save()
            self.language_preference = lang

        super().save(*args, **kwargs)


User = get_user_model()
# ======================================= User Profile Model =======================================
class UserProfileModel(BaseModel):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    
    # One-to-one relationship with User
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='profile')
    
    # Profile attributes
    profile_picture = ImageField(upload_to='profile_pictures/', null=True, blank=True)
    full_name = CharField(null=True, blank=True, max_length=255)  # Optional
    date_of_birth = DateField(null=True, blank=True)  # Optional - user can set later
    gender = CharField(null=True, blank=True, max_length=1, choices=GENDER_CHOICES)  # Optional
    annual_income = PositiveBigIntegerField(null=False, blank=False, default=1)  # required
    occupation = CharField(max_length=100, null=False, blank=False, default="Unknown")  # required
    
    # Calculate age from date of birth (Derived property)
    @property
    def age(self):
        if self.date_of_birth:
            today = date.today()
            if self.date_of_birth > today:
                return None
            return today.year - self.date_of_birth.year
        return None
            
    def __str__(self):
        return f"{self.user.mobile} Profile"

# ======================================= Bank Account Model =======================================
class BankAccountModel(BaseModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='bank_accounts')
    bank_name = CharField(max_length=100)
    account_number = CharField(max_length=20, unique=True)
    card_holder_name = CharField(max_length=100)
    ifsc_code = CharField(max_length=11) # IFSC isn't always unique per account — usually unique per branch
    bank_branch = CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

# ========================================= Address Model =========================================
class AddressModel(BaseModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='addresses')
    panchayat = CharField(max_length=100)
    village = CharField(max_length=100)
    city = CharField(max_length=100)
    zilla = CharField(max_length=100)
    state = CharField(max_length=100)
    pincode = CharField(max_length=20)
    full_address = TextField()

    def __str__(self):
        return f"{self.user.mobile} - {self.city}, {self.state}"

# ===================================== Government Details Model =====================================
class GovernmentDetailsModel(BaseModel):
    user = OneToOneField(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='government_details')
    aadhar_card_number = CharField(
        max_length=12, unique=True, null=True, blank=True, validators=[AADHAR_REGEX]
    )
    pan_card_number = CharField(
        max_length=10, unique=True, null=True, blank=True, validators=[PAN_REGEX]
    )
    gst_number = CharField(
        max_length=15, unique=True, null=True, blank=True, validators=[GST_REGEX]
    )
    
    aadhar_front_image = ImageField(upload_to='aadhaar_images/', null=True, blank=True)
    aadhar_back_image = ImageField(upload_to='aadhaar_images/', null=True, blank=True)
    
    pan_front_image = ImageField(upload_to='pan_images/', null=True, blank=True)

    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('VERIFIED', 'Verified'),
        ('FAILED', 'Failed'),
    ]
    aadhaar_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    pan_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    gst_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    income_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    occupation_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    overall_status = CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')

    def __str__(self):
        return f"{self.user.mobile} - Aadhar: {self.aadhar_card_number}, PAN: {self.pan_card_number}"

# ======================================= GST Model =======================================
class GSTModel(BaseModel):
    GST_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('SUSPENDED', 'Suspended'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    GST_TYPE_CHOICES = [
        ('REGULAR', 'Regular'),
        ('COMPOSITION', 'Composition'),
        ('CASUAL', 'Casual Taxable Person'),
        ('NON_RESIDENT', 'Non-Resident Taxable Person'),
    ]
    
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='gst_details')
    gst_number = CharField(
        max_length=15, unique=True, null=True, blank=True, validators=[GST_REGEX]
    )
    business_name = CharField(max_length=255)
    business_address = TextField()
    state_code = CharField(max_length=2)  # First 2 digits of GST number
    registration_date = DateField(null=True, blank=True)
    gst_status = CharField(max_length=20, choices=GST_STATUS_CHOICES, default='ACTIVE')
    gst_type = CharField(max_length=20, choices=GST_TYPE_CHOICES, default='REGULAR')
    annual_turnover = PositiveBigIntegerField(null=True, blank=True)
    is_verified = BooleanField(default=False)
    verification_date = DateTimeField(null=True, blank=True)
    
    # GST certificate document
    gst_certificate = FileField(upload_to='gst_certificates/', null=True, blank=True)
    
    class Meta:
        verbose_name = "GST Details"
        verbose_name_plural = "GST Details"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.mobile} - GST: {self.gst_number} ({self.business_name})"
    
    def save(self, *args, **kwargs):
        # Extract state code from GST number (first 2 digits)
        if self.gst_number and len(self.gst_number) >= 2:
            self.state_code = self.gst_number[:2]
        super().save(*args, **kwargs)

# ======================================= Customer Address Model =======================================
class CustomerAddressModel(BaseModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='customer_addresses')
    full_name = CharField(max_length=255)
    mobile_number = CharField(max_length=20)
    flat_house_building = CharField(max_length=255)
    area_street_village = CharField(max_length=255)
    pincode = CharField(max_length=10)
    town_city = CharField(max_length=100)
    state = CharField(max_length=100)
    is_default = BooleanField(default=False)

    def save(self, *args, **kwargs):
        # If this address is being set as default, unset other default addresses for this user
        if self.is_default:
            CustomerAddressModel.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.town_city}, {self.state}"

# ======================================= Search History Model =======================================
class SearchHistoryModel(BaseModel):
    user = ForeignKey(settings.AUTH_USER_MODEL, on_delete=CASCADE, related_name='search_history')
    query = CharField(max_length=200)
    
    class Meta:
        verbose_name = 'Search History'
        verbose_name_plural = 'Search Histories'
        ordering = ['-updated_at']
        unique_together = ('user', 'query')
        
    def __str__(self):
        return f"{self.user} searched for {self.query}"
