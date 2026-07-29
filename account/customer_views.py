from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login as auth_login
from account.models import User, GovernmentDetailsModel, RoleModel
from utils.functions import OTPHandler
from django.utils import timezone
from account.services import UserService
from django.contrib import messages
from account.models import CustomerAddressModel
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.sessions.models import Session
from django.conf import settings
import json

class CustomerLoginView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_login.html")

    def post(self, request, *args, **kwargs):
        aadhaar = request.POST.get("aadhaar")
        mobile = request.POST.get("mobile")

        if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
            return render(request, "account/customer_login.html", {"error": "Invalid Aadhaar Card Number."})
        
        if not mobile:
            return render(request, "account/customer_login.html", {"error": "Mobile number is required."})

        mobile = mobile if mobile.startswith("+91") else f"+91{mobile}"
        
        try:
            user = User.objects.get(mobile=mobile)
            user_role = user.roles.name if user.roles else 'Customer'
            if user_role != 'Customer':
                return render(request, "account/customer_login.html", {"error": f"This mobile number is registered as {user_role}. Please use a Customer account."})
            
            # Check aadhaar match if government details exist
            gov = GovernmentDetailsModel.objects.filter(user=user).first()
            if gov and gov.aadhar_card_number and gov.aadhar_card_number != aadhaar:
                return render(request, "account/customer_login.html", {"error": "Aadhaar number does not match our records for this mobile."})

        except User.DoesNotExist:
            # User doesn't exist, we will create them after OTP verification
            pass
        
        # Generate OTP
        OTPHandler.generate_otp(str(mobile), 'login')
        
        request.session['temp_customer_aadhaar'] = aadhaar
        request.session['temp_customer_mobile'] = mobile
        
        return redirect('customer_otp')


class CustomerOTPVerificationView(View):
    def get(self, request, *args, **kwargs):
        mobile = request.session.get('temp_customer_mobile')
        if not mobile:
            return redirect('customer_login')
        
        masked_mobile = f"********{mobile[-2:]}" if len(mobile) >= 2 else mobile
        return render(request, "account/customer_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile})

    def post(self, request, *args, **kwargs):
        mobile = request.session.get('temp_customer_mobile')
        aadhaar = request.session.get('temp_customer_aadhaar')
        
        if not mobile or not aadhaar:
            return redirect('customer_login')

        # Allow Resend OTP
        if "resend" in request.POST:
            OTPHandler.generate_otp(str(mobile), 'login')
            masked_mobile = f"********{mobile[-2:]}" if len(mobile) >= 2 else mobile
            return render(request, "account/customer_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "message": "OTP has been resent."})

        # We collect the single otp input
        otp = request.POST.get("otp", "").strip()
        
        if not otp:
            masked_mobile = f"********{mobile[-2:]}" if len(mobile) >= 2 else mobile
            return render(request, "account/customer_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "error": "Please enter the OTP."})

        try:
            OTPHandler.verifyOTP(mobile, 'login', otp)
            
            # Create user if does not exist
            try:
                user = User.objects.get(mobile=mobile)
                gov = GovernmentDetailsModel.objects.filter(user=user).first()
                if not gov:
                    gov = GovernmentDetailsModel(user=user)
                if not gov.aadhar_card_number:
                    gov.aadhar_card_number = aadhaar
                    gov.save()
            except User.DoesNotExist:
                role_obj, _ = RoleModel.objects.get_or_create(name='Customer')
                user = UserService.create({"mobile": mobile})
                user.roles = role_obj
                user.is_active = True
                user.save()
                
                gov = GovernmentDetailsModel(user=user, aadhar_card_number=aadhaar)
                gov.save()

            user.last_login = timezone.now()
            user.save()
            
            user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
            auth_login(request, user)
            
            # Clear session temp vars
            del request.session['temp_customer_aadhaar']
            del request.session['temp_customer_mobile']
            
            return redirect('customer_success')
            
        except Exception as e:
            masked_mobile = f"********{mobile[-2:]}" if len(mobile) >= 2 else mobile
            return render(request, "account/customer_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "error": "Invalid or expired OTP."})


class CustomerSuccessView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('customer_login')
        return render(request, "account/customer_success.html")

class CustomerMenuView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_menu.html")

class CustomerLoginSecurityView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_login_security.html")
        
    def post(self, request, *args, **kwargs):
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        
        user = request.user
        if fullname is not None:
            user.fullname = fullname.strip()
        if email is not None:
            user.email = email.strip()
            
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('customer_login_security')

class CustomerLegalAboutView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_legal_about.html")

class CustomerPrivacyNoticeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_privacy_notice.html")

class CustomerAddressListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        addresses = CustomerAddressModel.objects.filter(user=request.user)
        return render(request, "account/customer_address_list.html", {"addresses": addresses})

class CustomerAddressCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/customer_address_form.html", {"is_edit": False})
        
    def post(self, request, *args, **kwargs):
        full_name = request.POST.get('full_name')
        mobile_number = request.POST.get('mobile_number')
        flat_house_building = request.POST.get('flat_house_building')
        area_street_village = request.POST.get('area_street_village')
        pincode = request.POST.get('pincode')
        town_city = request.POST.get('town_city')
        state = request.POST.get('state')
        is_default = request.POST.get('is_default') == 'on'
        
        CustomerAddressModel.objects.create(
            user=request.user,
            full_name=full_name,
            mobile_number=mobile_number,
            flat_house_building=flat_house_building,
            area_street_village=area_street_village,
            pincode=pincode,
            town_city=town_city,
            state=state,
            is_default=is_default
        )
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('customer_address_list')

class CustomerAddressUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        address = get_object_or_404(CustomerAddressModel, pk=pk, user=request.user)
        return render(request, "account/customer_address_form.html", {"is_edit": True, "address": address})
        
    def post(self, request, pk, *args, **kwargs):
        address = get_object_or_404(CustomerAddressModel, pk=pk, user=request.user)
        address.full_name = request.POST.get('full_name')
        address.mobile_number = request.POST.get('mobile_number')
        address.flat_house_building = request.POST.get('flat_house_building')
        address.area_street_village = request.POST.get('area_street_village')
        address.pincode = request.POST.get('pincode')
        address.town_city = request.POST.get('town_city')
        address.state = request.POST.get('state')
        address.is_default = request.POST.get('is_default') == 'on'
        address.save()
        next_url = request.POST.get('next')
        if next_url:
            return redirect(next_url)
        return redirect('customer_address_list')

class CustomerAddressDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        address = get_object_or_404(CustomerAddressModel, pk=pk, user=request.user)
        was_default = address.is_default
        address.delete()
        if was_default:
            other_address = CustomerAddressModel.objects.filter(user=request.user).first()
            if other_address:
                other_address.is_default = True
                other_address.save()
        return redirect('customer_address_list')

class CustomerAddressSetDefaultView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        from django.http import JsonResponse
        address = get_object_or_404(CustomerAddressModel, pk=pk, user=request.user)
        address.is_default = True
        address.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True})
        return redirect('customer_address_list')

class CustomerDeleteAccountView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mobile = request.user.mobile
        OTPHandler.generate_otp(str(mobile), 'login')
        masked_mobile = f"******{str(mobile)[-4:]}" if len(str(mobile)) >= 4 else str(mobile)
        return render(request, "account/customer_delete_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile})

    def post(self, request, *args, **kwargs):
        mobile = request.user.mobile
        
        if "resend" in request.POST:
            OTPHandler.generate_otp(str(mobile), 'login')
            masked_mobile = f"******{str(mobile)[-4:]}" if len(str(mobile)) >= 4 else str(mobile)
            return render(request, "account/customer_delete_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "message": "OTP has been resent."})

        otp_parts = []
        for i in range(1, 5):
            part = request.POST.get(f"otp{i}", "").strip()
            if part:
                otp_parts.append(part)
        
        otp = "".join(otp_parts)
        
        if not otp:
            masked_mobile = f"******{str(mobile)[-4:]}" if len(str(mobile)) >= 4 else str(mobile)
            return render(request, "account/customer_delete_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "error": "Please enter the OTP."})

        try:
            OTPHandler.verifyOTP(str(mobile), 'login', otp)
            
            user = request.user
            user.delete()
            
            return redirect('customer_login')
            
        except Exception as e:
            masked_mobile = f"******{str(mobile)[-4:]}" if len(str(mobile)) >= 4 else str(mobile)
            return render(request, "account/customer_delete_otp_verification.html", {"masked_mobile": masked_mobile, "mobile": mobile, "error": "Invalid or expired OTP."})

class CustomerSwitchAccountView(View):
    def get(self, request, *args, **kwargs):
        # We allow viewing this page even if not strictly authenticated, 
        # but usually you access it when authenticated.
        cookie_name = 'garud_customer_accounts'
        saved_accounts_str = request.COOKIES.get(cookie_name, '{}')
        try:
            saved_accounts = json.loads(saved_accounts_str)
        except json.JSONDecodeError:
            saved_accounts = {}
            
        active_user_id = str(request.user.id) if request.user.is_authenticated else None
        
        accounts_list = []
        for uid, data in saved_accounts.items():
            data['is_active'] = (uid == active_user_id)
            accounts_list.append(data)
            
        # Sort so active is first, then by name
        accounts_list.sort(key=lambda x: (not x['is_active'], x.get('name', '')))
        
        return render(request, "account/customer_switch_account.html", {"accounts": accounts_list})

class CustomerSwitchAccountActionView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'No user_id provided'}, status=400)
            
        if request.user.is_authenticated and str(request.user.id) == str(user_id):
            # Already active
            return JsonResponse({'status': 'switched'})
            
        cookie_name = 'garud_customer_accounts'
        saved_accounts_str = request.COOKIES.get(cookie_name, '{}')
        try:
            saved_accounts = json.loads(saved_accounts_str)
        except json.JSONDecodeError:
            saved_accounts = {}
            
        target_account = saved_accounts.get(str(user_id))
        if not target_account:
            return JsonResponse({'status': 'error', 'message': 'Account not found'}, status=404)
            
        session_key = target_account.get('session_key')
        is_valid = False
        
        if session_key:
            # Check if session exists and is valid in DB
            try:
                session_obj = Session.objects.get(session_key=session_key)
                if session_obj.expire_date > timezone.now():
                    is_valid = True
            except Session.DoesNotExist:
                pass
                
        if is_valid:
            # Swap session by telling the frontend to reload after we set the cookie
            # Actually, doing it via JsonResponse is hard because the browser needs to set the sessionid cookie.
            # We can set the cookie in the response.
            response = JsonResponse({'status': 'switched'})
            response.set_cookie(settings.SESSION_COOKIE_NAME, session_key, max_age=settings.SESSION_COOKIE_AGE, httponly=True)
            return response
        else:
            # Expired session -> generate OTP
            mobile = target_account.get('mobile')
            if not mobile:
                return JsonResponse({'status': 'error', 'message': 'Mobile number missing'}, status=400)
                
            OTPHandler.generate_otp(mobile, 'login')
            request.session['temp_customer_mobile'] = mobile
            # Need the aadhaar from db to re-login if necessary, or just not require it for switch
            # We can find the user to get aadhaar
            try:
                user = User.objects.get(id=user_id)
                gov = GovernmentDetailsModel.objects.filter(user=user).first()
                if gov and gov.aadhar_card_number:
                    request.session['temp_customer_aadhaar'] = gov.aadhar_card_number
            except User.DoesNotExist:
                pass
                
            return JsonResponse({'status': 'requires_otp', 'redirect_url': '/customer/otp-verification/'})

class CustomerSwitchAccountRemoveView(View):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        if not user_id:
            return JsonResponse({'status': 'error', 'message': 'No user_id provided'}, status=400)
            
        cookie_name = 'garud_customer_accounts'
        saved_accounts_str = request.COOKIES.get(cookie_name, '{}')
        try:
            saved_accounts = json.loads(saved_accounts_str)
        except json.JSONDecodeError:
            saved_accounts = {}
            
        if str(user_id) in saved_accounts:
            del saved_accounts[str(user_id)]
            
        response = JsonResponse({'status': 'removed'})
        response.set_cookie(cookie_name, json.dumps(saved_accounts), max_age=31536000, httponly=True, samesite='Lax')
        return response
