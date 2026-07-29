from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import User
from .services import UserService
from utils.functions import OTPHandler
from decimal import Decimal
from django.http import JsonResponse

def register(request):
    message = ""
    role = request.GET.get('role', 'Customer')
    if request.method == "POST":
        data = request.POST.dict()
        if not data.get("mobile").startswith("+91"):
            data["mobile"] = "+91" + data.get("mobile")
        try:
            # We must assign the role
            from account.models import RoleModel
            role_obj, _ = RoleModel.objects.get_or_create(name=role)
            user = UserService.create(data)
            user.roles = role_obj
            user.save()
            
            message = "Registration successful. Please login."
            return redirect(f'/accounts/login/?role={role}')
        except Exception as e:
            message = str(e)
    return render(request, "account/register.html", {"message": message, "role": role})

def login_view(request):
    message = ""
    role = request.GET.get('role', 'Customer')
    
    if request.method == "POST":
        mobile = request.POST.get("mobile")
        otp = request.POST.get("otp")
        mpin = request.POST.get("mpin")
        otp_forgot = request.POST.get("otp_forgot")

        mobile = mobile if mobile.startswith("+91") else f"+91{mobile}"
        # Step 1: Only mobile submitted
        if mobile and not otp and not mpin and not otp_forgot:
            try:
                user = User.objects.get(mobile=mobile)
                # Check role mismatch
                user_role = user.roles.name if user.roles else 'Customer'
                if user_role != role:
                    message = f"यह खाता {user_role} खाते के रूप में पंजीकृत है। (This account is registered as a {user_role} account.)"
                    return render(request, "account/login.html", {"message": message, "role": role})

                if role == 'Seller':
                    ask_mpin = False # Force OTP for Sellers
                else:
                    ask_mpin = user.has_usable_password()
            except User.DoesNotExist:
                if role == 'Seller':
                    message = "खाता नहीं मिला। कृपया नया खाता बनाएं। (Account not found. Please create a new account.)"
                    return render(request, "account/login.html", {"message": message, "role": role})
                ask_mpin = False
 
            # Render OTP or MPIN page
            OTPHandler.generate_otp(str(mobile), 'login') if not ask_mpin else None

            return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": ask_mpin, "role": role})
        # Step 2: Forgot MPIN flow (OTP for MPIN reset)
        if mobile and otp_forgot:
            try:
                user = User.objects.get(mobile=mobile)
                OTPHandler.verifyOTP(mobile, 'login', otp_forgot)
                user.last_login = timezone.now()
                user.save()
                user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
                auth_login(request, user)
                from account.views import role_aware_redirect
                response = redirect('set_mpin')
                if user.language_preference:
                    response.set_cookie('garuda_language', user.language_preference.name, max_age=365*24*60*60)
                return response
            except User.DoesNotExist:
                message = "User does not exist."
            except Exception as e:
                message = str(e)

            OTPHandler.generate_otp(mobile, 'login')
            return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": True, "message": message, "role": role})
        # Step 3: Mobile + OTP/MPIN submitted
        if mobile and (otp or mpin):
            try:
                user = User.objects.get(mobile=mobile)
                if not user.is_active:
                    if not otp:
                        message = "Account is deactivated. Login with OTP only."
                        return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": False, "message": message, "role": role})
                    OTPHandler.verifyOTP(mobile, 'login', otp)
                    user.is_active = True

                    user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
                    auth_login(request, user)
                    if role != 'Seller' and not user.has_usable_password():
                        response = redirect('set_mpin')
                    else:
                        response = redirect('central_controller')
                    if user.language_preference:
                        response.set_cookie('garuda_language', user.language_preference.name, max_age=365*24*60*60)
                    return response
                else:
                    if mpin and user.check_password(mpin) and role != 'Seller':                        
                        user.save()

                        user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
                        auth_login(request, user)
                        response = redirect('central_controller')
                        if user.language_preference:
                            response.set_cookie('garuda_language', user.language_preference.name, max_age=365*24*60*60)
                        return response
                    elif otp:
                        OTPHandler.verifyOTP(mobile, 'login', otp)
                        user.last_login = timezone.now()
                        user.save()

                        user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
                        auth_login(request, user)
                        if role != 'Seller' and not user.has_usable_password():
                            response = redirect('set_mpin')
                        else:
                            response = redirect('central_controller')
                        if user.language_preference:
                            response.set_cookie('garuda_language', user.language_preference.name, max_age=365*24*60*60)
                        return response
                    else:
                        message = "OTP or MPIN required." if role != 'Seller' else "OTP required."
                        return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": user.has_usable_password() if role != 'Seller' else False, "message": message, "role": role})
            except User.DoesNotExist:
                if role == 'Seller':
                    message = "खाता नहीं मिला। कृपया नया खाता बनाएं। (Account not found. Please create a new account.)"
                    return render(request, "account/login.html", {"message": message, "role": role})
                if otp:
                    OTPHandler.verifyOTP(mobile, 'login', otp)
                    user = UserService.create({"mobile": mobile})
                    user.last_login = timezone.now()
                    user.save()

                    user.backend = 'account.authentication.PINPasswordAuthenticationBackend'
                    auth_login(request, user)
                    response = redirect('set_mpin')
                    if user.language_preference:
                        response.set_cookie('garuda_language', user.language_preference.name, max_age=365*24*60*60)
                    return response
                else:
                    message = "OTP required for registration."
                    return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": False, "message": message, "role": role})
            except Exception as e:
                message = str(e)
                return render(request, "account/otp_or_mpin.html", {"mobile": mobile, "ask_mpin": user.has_usable_password() if 'user' in locals() and role != 'Seller' else False, "message": message, "role": role})
        # Fallback: show login page
        message = "Mobile number required."
    return render(request, "account/login.html", {"message": message, "role": role})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def profile(request):
    return render(request, "success/success.html", {"css_file": "static/css/success.css"})
#     message = ""
#     user = request.user
#     if request.method == "POST":
#         # Handle photo upload 
#         if request.FILES.get("photo"):
#             UserService.update_photo(user.pk, request.FILES["photo"])
#             message = "Photo updated."
#         else:
#             # Handle profile info update
#             fullname = request.POST.get("fullname")
#             mobile = request.POST.get("mobile")
#             mobile_otp = request.POST.get("mobile_otp")
#             email = request.POST.get("email")
#             email_otp = request.POST.get("email_otp")
#             data = {
#                 "fullname": fullname,
#                 "mobile": mobile,
#                 "mobile_otp": mobile_otp,
#                 "email": email,
#                 "email_otp": email_otp,
#             }
#             try:
#                 UserService.update(user.pk, data)
#                 message = "Profile updated."
#             except Exception as e:
#                 message = str(e)


@login_required
def set_mpin_view(request):
    message = ""
    if request.method == "POST":
        mpin = request.POST.get("mpin")
        mpin2 = request.POST.get("mpin2")
        if not mpin or not mpin2:
            message = "Both fields are required."
        elif mpin != mpin2:
            message = "MPINs do not match."
        elif not mpin.isdigit() or len(mpin) != 4:
            message = "MPIN must be a 4-digit number."
        else:
            user = request.user
            user.set_password(mpin)
            user.save()
            return redirect('central_controller')
    return render(request, "account/set_mpin.html", {"message": message})
