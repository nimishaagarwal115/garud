from django import forms
from account.models import (                            
                            UserProfileModel, 
                            GovernmentDetailsModel, 
                            LanguagePreferenceModel, 
                            BankAccountModel, 
                            AddressModel,
                            GSTModel
                        )
from django.contrib.auth import get_user_model
User = get_user_model()
# ==================================================== Reusable Widgets & Helpers ====================================================

def text_input_widget(placeholder='', extra_classes=''):
    return forms.TextInput(attrs={
        'placeholder': placeholder,
        'class': f'form-control {extra_classes}'.strip()
    })

def date_input_widget():
    return forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})

def select_widget():
    return forms.Select(attrs={'class': 'form-control'})

def radio_widget():
    return forms.RadioSelect(attrs={'class': 'form-check-input'})

# ============================================================ Auth Forms ============================================================

class CookieConsentForm(forms.Form):
    pass

class PhoneLoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['mobile']
        widgets = {
            'mobile': text_input_widget('Phone Number'),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data['mobile'].replace(" ", "")
        if not phone.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        return phone

class OTPVerifyForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i in range(1, 7):
            attrs = {
                'class': 'otp-field',
                'maxlength': '1',
                'autocomplete': 'off',
                'inputmode': 'numeric',
            }

            # Only add onclick if needed
            if i<6:
                attrs['oninput'] = f'moveToNext(this, "id_send_password_otp{i+1}");'

            self.fields[f'send_password_otp{i}'].widget.attrs.update(attrs)

    send_password_otp1 = forms.CharField(max_length=1, required=True)
    send_password_otp2 = forms.CharField(max_length=1, required=True)
    send_password_otp3 = forms.CharField(max_length=1, required=True)
    send_password_otp4 = forms.CharField(max_length=1, required=True)
    send_password_otp5 = forms.CharField(max_length=1, required=True)
    send_password_otp6 = forms.CharField(max_length=1, required=True)

    def clean(self):
        cleaned_data = super().clean()
        otp = ''.join([
            cleaned_data.get("send_password_otp1", ""),
            cleaned_data.get("send_password_otp2", ""),
            cleaned_data.get("send_password_otp3", ""),
            cleaned_data.get("send_password_otp4", ""),
            cleaned_data.get("send_password_otp5", ""),
            cleaned_data.get("send_password_otp6", ""),
        ])
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("Enter a valid 6-digit OTP.")
        cleaned_data["send_password_otp"] = otp
        return cleaned_data

# ======================================================= Profile & User Forms =======================================================

class UserProfileForm(forms.ModelForm):
    age = forms.IntegerField(
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'उम्र', 'min': 18, 'max': 100})
    )

    class Meta:
        model = UserProfileModel
        fields = ['full_name', 'gender', 'annual_income', 'occupation']
        widgets = {
            'full_name': text_input_widget('Full Name'),
            'gender': select_widget(),
            'annual_income': text_input_widget('Example: Rs 50,000'),
            'occupation': text_input_widget('Occupation'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.age:
            self.initial['age'] = self.instance.age

    def save(self, commit=True):
        instance = super().save(commit=False)
        age = self.cleaned_data.get('age')
        if age:
            from datetime import date
            today = date.today()
            instance.date_of_birth = date(today.year - age, 1, 1)
        if commit:
            instance.save()
        return instance

class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['mobile', 'photo']
        widgets = {
            'mobile': text_input_widget('Phone Number'),
            'photo': forms.FileInput(attrs={'style': 'display: none;', 'id': 'id_profile_picture'}),
        }

class GSTBusinessNameForm(forms.ModelForm):
    class Meta:
        model = GSTModel
        fields = ['business_name']
        widgets = {
            'business_name': text_input_widget('Shop / Business Name'),
        }

class GovernmentDetailsForm(forms.ModelForm):
    class Meta:
        model = GovernmentDetailsModel
        fields = ['aadhar_card_number', 'pan_card_number', 'gst_number']
        widgets = {
            'aadhar_card_number': text_input_widget('Aadhaar Card Number'),
            'pan_card_number': text_input_widget('PAN Card Number'),
            'gst_number': text_input_widget('GST Number'),
        }

class AadhaarOnlyForm(forms.ModelForm):
    class Meta:
        model = GovernmentDetailsModel
        fields = ['aadhar_card_number']
        widgets = {
            'aadhar_card_number': text_input_widget('Enter your 12-digit Aadhaar Number'),
        }

    def clean_aadhar_card_number(self):
        aadhar = self.cleaned_data.get('aadhar_card_number')
        if not aadhar.isdigit() or len(aadhar) != 12:
            raise forms.ValidationError("Aadhaar must be exactly 12 digits.")
        if GovernmentDetailsModel.objects.filter(aadhar_card_number=aadhar).exists():
            raise forms.ValidationError("This Aadhaar number is already registered.")
        return aadhar

class AnnualIncomeForm(forms.ModelForm):
    class Meta:
        model = UserProfileModel
        fields = ['annual_income']  # Only include annual_income field
        widgets = {
            'annual_income': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg', 
                'placeholder': 'Enter your annual income',
                'min': '0',
                'step': '1'
            }),
        }
    
    def clean_annual_income(self):
        annual_income = self.cleaned_data.get('annual_income')
        if annual_income is not None and annual_income < 0:
            raise forms.ValidationError("Annual income cannot be negative.")
        return annual_income

class OccupationForm(forms.ModelForm):
    class Meta:
        model = UserProfileModel
        fields = ['occupation']
        widgets = {
            'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}),
        }

# class AnnualIncomeOccupationForm(forms.ModelForm):
#     class Meta:
#         model = UserProfileModel
#         fields = ['annual_income', 'occupation']
#         widgets = {
#             'annual_income': forms.NumberInput(attrs={
#                 'class': 'form-control form-control-lg', 
#                 'placeholder': 'Enter your annual income',
#                 'min': '0',
#                 'step': '1'
#             }),
#             'occupation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Occupation'}),
#         }
    
#     def clean_annual_income(self):
#         annual_income = self.cleaned_data.get('annual_income')
#         if annual_income is not None and annual_income < 0:
#             raise forms.ValidationError("Annual income cannot be negative.")
#         return annual_income
    
#     def clean_occupation(self):
#         occupation = self.cleaned_data.get('occupation')
#         if not occupation or occupation.strip() == '':
#             raise forms.ValidationError("Occupation is required.")
#         return occupation.strip()

# ================================================== Preferences & Settings Forms ==================================================

class LanguagePreferenceForm(forms.Form):
    language = forms.ModelChoiceField(
        queryset=LanguagePreferenceModel.objects.all(),
        empty_label=None,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )

class AddressForm(forms.ModelForm):
    class Meta:
        model = AddressModel
        fields = ['panchayat', 'village', 'city', 'zilla', 'state', 'pincode', 'full_address']
        widgets = {field: text_input_widget() for field in fields}

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccountModel
        fields = ['bank_name', 'account_number', 'card_holder_name', 'ifsc_code']
        widgets = {field: text_input_widget() for field in fields}

class AadhaarForm(forms.ModelForm):
    class Meta:
        model = GovernmentDetailsModel
        fields = '__all__'
        widgets = {
            'aadhar_card_number': forms.TextInput(attrs={'placeholder': 'Enter your 12-digit Aadhaar Number', 'class': 'form-control'}),
            'aadhar_front_image': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
            'aadhar_back_image': forms.ClearableFileInput(attrs={'accept': 'image/*', 'class': 'form-control'}),
        }

    def clean_aadhar_card_number(self):
        aadhar = self.cleaned_data.get('aadhar_card_number')
        if not aadhar or not aadhar.isdigit() or len(aadhar) != 12:
            raise forms.ValidationError("Aadhaar must be exactly 12 digits.")
        
        # Check if Aadhaar already exists for a different user (exclude current instance)
        existing_aadhaar = GovernmentDetailsModel.objects.filter(aadhar_card_number=aadhar)
        if self.instance and self.instance.pk:
            existing_aadhaar = existing_aadhaar.exclude(pk=self.instance.pk)
        
        if existing_aadhaar.exists():
            raise forms.ValidationError("This Aadhaar number is already registered.")
        return aadhar

class GSTNumberForm(forms.ModelForm):
    class Meta:
        model = GovernmentDetailsModel
        fields = ['gst_number']
        widgets = {
            'gst_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter GST Number (optional)'}),
        }

class PANCardForm(forms.ModelForm):
    class Meta:
        model = GovernmentDetailsModel
        fields = ['pan_card_number']
        widgets = {
            'pan_card_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter PAN Card Number (e.g. ABCDE1234F)',
                'style': 'text-transform: uppercase;'
            }),
        }
    
    def clean_pan_card_number(self):
        pan = self.cleaned_data.get('pan_card_number')
        if pan:
            pan = pan.upper().strip()
            
            # Validate PAN format: 5 letters, 4 digits, 1 letter
            import re
            pan_regex = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')
            if not pan_regex.match(pan):
                raise forms.ValidationError("PAN must be in format: 5 letters, 4 digits, 1 letter (e.g., ABCDE1234F)")
            
            # Check if PAN already exists for a different user (exclude current instance)
            existing_pan = GovernmentDetailsModel.objects.filter(pan_card_number=pan)
            if self.instance and self.instance.pk:
                existing_pan = existing_pan.exclude(pk=self.instance.pk)
            
            if existing_pan.exists():
                raise forms.ValidationError("This PAN number is already registered.")
        
        return pan

# ==================================================== Phone Number Confirmation Form ====================================================

class PhoneConfirmationForm(forms.Form):
    ACTION_CHOICES = [
        ('continue', 'Continue with current number'),
        ('change', 'Change phone number'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    new_phone_number = forms.CharField(
        max_length=14,
        required=False,
        widget=text_input_widget('Enter new phone number'),
        help_text='Only required if changing phone number'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        new_phone_number = cleaned_data.get('new_phone_number')
        
        if action == 'change':
            if not new_phone_number:
                raise forms.ValidationError("Please enter a new phone number.")
            
            # Clean and validate the new phone number
            new_phone_number = new_phone_number.replace(" ", "")
            if not new_phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            
            if len(new_phone_number) < 10:
                raise forms.ValidationError("Phone number must have at least 10 digits.")
            
            cleaned_data['new_phone_number'] = new_phone_number
        
        return cleaned_data


# ==================================================== Reusable Widgets & Helpers ====================================================