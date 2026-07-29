from django.views import View

from multiprocessing import context
from time import timezone
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.shortcuts import render, redirect, get_object_or_404
import sys
import subprocess

try:
    import google.generativeai
except ImportError:
    print("Installing missing google-generativeai package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
        print("Successfully installed google-generativeai.")
    except Exception as e:
        print(f"Failed to auto-install google-generativeai: {e}")

from django.db.models import Q
from django.views.generic import TemplateView, View, RedirectView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from catalogue.models import *
import pytesseract
import requests
import os
import requests
import http.client
import json
import base64
import json
import cv2 
import tempfile
import re
import traceback
import uuid
from django.utils.decorators import method_decorator

from account.models import *
from account.forms import *
from django.views.generic import (
    FormView, 
    TemplateView, 
    CreateView, 
    UpdateView,
    DeleteView,
    ListView
)
from catalogue.models import *

from core.base.views import (
    BaseTemplateView, 
    AuthenticatedRedirectMixin, 
    BaseDashboardView
)
from core.base.utils import (
    send_sms_otp,
    validate_otp
)
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from account.mixins import CustomerRequiredMixin, SellerRequiredMixin

from orders.models import *
User = get_user_model()
# ================================================== Entry Flow Views ==================================================
class SplashView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/splash.html')

class SellerWelcomeView(SellerRequiredMixin, TemplateView):
    template_name = 'seller/welcome.html'

class SellerOnboardingStepperView(View):
    def get(self, request, step, *args, **kwargs):
        # Gather cumulative data to display on confirmation screens
        user = request.user
        onboarding_data = request.session.get('onboarding_data', {})
        
        if user.is_authenticated:
            photo_url = user.photo.url if user.photo else None
            profile = getattr(user, 'profile', None)
            name = profile.full_name if profile else ""
            gov = getattr(user, 'government_details', None)
            aadhaar = gov.aadhar_card_number if gov else ""
            gst = gov.gst_number if gov else ""
            gst_model = user.gst_details.first() if hasattr(user, 'gst_details') else None
            shop_name = gst_model.business_name if gst_model else ""
            addr_model = user.addresses.first() if hasattr(user, 'addresses') else None
            address = addr_model.full_address if addr_model else ""
            city = addr_model.city if addr_model else ""
            zilla = addr_model.zilla if addr_model else ""
            state = addr_model.state if addr_model else ""
            pincode = addr_model.pincode if addr_model else ""
            bank_model = user.bank_accounts.first() if hasattr(user, 'bank_accounts') else None
            account_number = bank_model.account_number if bank_model else ""
            ifsc_code = bank_model.ifsc_code if bank_model else ""
            card_holder_name = bank_model.card_holder_name if bank_model else ""
            mobile_number = user.mobile
        else:
            photo_url = onboarding_data.get('photo_url', None)
            name = onboarding_data.get('name', '')
            aadhaar = onboarding_data.get('aadhaar', '')
            gst = onboarding_data.get('gst', '')
            shop_name = onboarding_data.get('shop_name', '')
            address = onboarding_data.get('address', '')
            city = onboarding_data.get('city', '')
            zilla = onboarding_data.get('zilla', '')
            state = onboarding_data.get('state', '')
            pincode = onboarding_data.get('pincode', '')
            account_number = onboarding_data.get('account_number', '')
            ifsc_code = onboarding_data.get('ifsc_code', '')
            card_holder_name = onboarding_data.get('card_holder_name', '')
            mobile_number = onboarding_data.get('aadhaar_mobile', '')
        
        context = {
            'step': step,
            'photo_url': photo_url,
            'user_name': name,
            'aadhaar_number': aadhaar,
            'mobile_number': mobile_number,
            'gst_number': gst,
            'shop_name': shop_name,
            'address': address,
            'city': city,
            'zilla': zilla,
            'state': state,
            'pincode': pincode,
            'account_number': account_number,
            'ifsc_code': ifsc_code,
            'card_holder_name': card_holder_name,
        }
        
        template_name = f'seller/onboarding_step_{step}.html'
        return render(request, template_name, context)

    def post(self, request, step, *args, **kwargs):
        user = request.user
        onboarding_data = request.session.get('onboarding_data', {})
        
        if step == 1:
            if 'photo' in request.FILES:
                if user.is_authenticated:
                    user.photo = request.FILES['photo']
                    user.save()
                else:
                    from django.core.files.storage import FileSystemStorage
                    fs = FileSystemStorage()
                    photo = request.FILES['photo']
                    filename = fs.save(photo.name, photo)
                    onboarding_data['photo_url'] = fs.url(filename)
                    onboarding_data['photo_path'] = fs.path(filename)
        elif step == 2:
            name = request.POST.get('name')
            if name:
                if user.is_authenticated:
                    profile, _ = UserProfileModel.objects.get_or_create(user=user)
                    profile.full_name = name
                    profile.save()
                else:
                    onboarding_data['name'] = name
        elif step == 3:
            aadhaar = request.POST.get('aadhaar')
            if aadhaar:
                if user.is_authenticated:
                    gov, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                    gov.aadhar_card_number = aadhaar
                    gov.save()
                else:
                    onboarding_data['aadhaar'] = aadhaar
        elif step == 4:
            aadhaar_mobile = request.POST.get('aadhaar_mobile')
            if aadhaar_mobile:
                aadhaar_mobile = aadhaar_mobile if aadhaar_mobile.startswith("+91") else f"+91{aadhaar_mobile}"
                if not user.is_authenticated:
                    # Validate mobile number uniqueness
                    from account.models import User
                    if User.objects.filter(mobile=aadhaar_mobile).exists():
                        # Duplicate mobile, redirect back to step 4 with an error?
                        # Since we can't easily pass error context without changing template, we can use messages
                        from django.contrib import messages
                        messages.error(request, 'This mobile number is already registered.')
                        return redirect('seller_onboarding_step', step=step)
                onboarding_data['aadhaar_mobile'] = aadhaar_mobile
        elif step == 5:
            gst = request.POST.get('gst')
            if gst:
                if user.is_authenticated:
                    gov, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                    gov.gst_number = gst
                    gov.save()
                    gst_model, _ = GSTModel.objects.get_or_create(user=user, defaults={'gst_number': None})
                    if gst:
                        gst_model.gst_number = gst
                    else:
                        gst_model.gst_number = None
                    gst_model.save()
                else:
                    onboarding_data['gst'] = gst
        elif step == 6:
            shop_name = request.POST.get('shop_name')
            if shop_name:
                if user.is_authenticated:
                    gst_model, _ = GSTModel.objects.get_or_create(user=user, defaults={'gst_number': None})
                    gst_model.business_name = shop_name
                    gst_model.save()
                else:
                    onboarding_data['shop_name'] = shop_name
        elif step == 7:
            address = request.POST.get('address')
            pincode = request.POST.get('pincode')
            city = request.POST.get('city')
            zilla = request.POST.get('zilla')
            state = request.POST.get('state')
            
            if user.is_authenticated:
                if address or pincode or city or zilla or state:
                    addr_model, _ = AddressModel.objects.get_or_create(
                        user=user,
                        defaults={
                            'panchayat': '', 'village': '', 'city': '', 'zilla': '', 'state': '', 'pincode': '', 'full_address': ''
                        }
                    )
                    if address: addr_model.full_address = address
                    if pincode: addr_model.pincode = pincode
                    if city: addr_model.city = city
                    if zilla: addr_model.zilla = zilla
                    if state: addr_model.state = state
                    addr_model.save()
            else:
                onboarding_data['address'] = address
                onboarding_data['pincode'] = pincode
                onboarding_data['city'] = city
                onboarding_data['zilla'] = zilla
                onboarding_data['state'] = state
        elif step == 8:
            if user.is_authenticated:
                # Existing user finalizing onboarding
                name = request.POST.get('name')
                aadhaar = request.POST.get('aadhaar')
                gst = request.POST.get('gst')
                shop_name = request.POST.get('shop_name')
                address = request.POST.get('address')
                pincode = request.POST.get('pincode')
                city = request.POST.get('city')
                zilla = request.POST.get('zilla')
                state = request.POST.get('state')
                account_number = request.POST.get('account_number')
                ifsc_code = request.POST.get('ifsc_code')
                card_holder_name = request.POST.get('card_holder_name')
                
                if name:
                    profile, _ = UserProfileModel.objects.get_or_create(user=user)
                    profile.full_name = name
                    profile.save()
                
                gov, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                if aadhaar:
                    gov.aadhar_card_number = aadhaar
                if gst:
                    gov.gst_number = gst
                gov.overall_status = 'UPLOADED'
                gov.save()
                
                if gst or shop_name:
                    gst_model, _ = GSTModel.objects.get_or_create(user=user, defaults={'gst_number': None})
                    if gst: 
                        gst_model.gst_number = gst
                    else:
                        gst_model.gst_number = None
                    if shop_name: gst_model.business_name = shop_name
                    gst_model.save()
                    
                if address or pincode or city or zilla or state:
                    addr_model, _ = AddressModel.objects.get_or_create(
                        user=user,
                        defaults={
                            'panchayat': '', 'village': '', 'city': '', 'zilla': '', 'state': '', 'pincode': '', 'full_address': ''
                        }
                    )
                    if address: addr_model.full_address = address
                    if pincode: addr_model.pincode = pincode
                    if city: addr_model.city = city
                    if zilla: addr_model.zilla = zilla
                    if state: addr_model.state = state
                    addr_model.save()
                    
                if account_number or ifsc_code or card_holder_name:
                    bank_model, _ = BankAccountModel.objects.get_or_create(user=user)
                    if account_number: bank_model.account_number = account_number
                    if ifsc_code: bank_model.ifsc_code = ifsc_code
                    if card_holder_name: bank_model.card_holder_name = card_holder_name
                    bank_model.save()
                    
                return redirect('onboarding_success')
            else:
                # Process final review for unauthenticated user
                onboarding_data['name'] = request.POST.get('name', onboarding_data.get('name', ''))
                onboarding_data['aadhaar'] = request.POST.get('aadhaar', onboarding_data.get('aadhaar', ''))
                onboarding_data['gst'] = request.POST.get('gst', onboarding_data.get('gst', ''))
                onboarding_data['shop_name'] = request.POST.get('shop_name', onboarding_data.get('shop_name', ''))
                onboarding_data['address'] = request.POST.get('address', onboarding_data.get('address', ''))
                onboarding_data['pincode'] = request.POST.get('pincode', onboarding_data.get('pincode', ''))
                onboarding_data['city'] = request.POST.get('city', onboarding_data.get('city', ''))
                onboarding_data['zilla'] = request.POST.get('zilla', onboarding_data.get('zilla', ''))
                onboarding_data['state'] = request.POST.get('state', onboarding_data.get('state', ''))
                onboarding_data['account_number'] = request.POST.get('account_number', onboarding_data.get('account_number', ''))
                onboarding_data['ifsc_code'] = request.POST.get('ifsc_code', onboarding_data.get('ifsc_code', ''))
                onboarding_data['card_holder_name'] = request.POST.get('card_holder_name', onboarding_data.get('card_holder_name', ''))
                
                # Create Account
                mobile = onboarding_data.get('aadhaar_mobile')
                if not mobile:
                    return redirect('seller_onboarding_step', step=4)
                    
                from account.models import RoleModel
                role_obj, _ = RoleModel.objects.get_or_create(name='Seller')
                
                from account.models import User
                from account.services import UserService
                from django.db import transaction
                
                with transaction.atomic():
                    user = User.objects.filter(mobile=mobile).first()
                    if not user:
                        user = UserService.create({"mobile": mobile})
                    user.roles = role_obj
                
                    if onboarding_data.get('photo_path'):
                        from django.core.files import File
                        import os
                        if os.path.exists(onboarding_data['photo_path']):
                            with open(onboarding_data['photo_path'], 'rb') as f:
                                user.photo.save(os.path.basename(onboarding_data['photo_path']), File(f))
                    user.save()
                    
                    profile, _ = UserProfileModel.objects.get_or_create(user=user)
                    profile.full_name = onboarding_data.get('name', '')
                    profile.save()
                    
                    gov, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                    aadhaar_val = onboarding_data.get('aadhaar', '')
                    gov.aadhar_card_number = aadhaar_val if aadhaar_val else None
                    gst_val = onboarding_data.get('gst', '')
                    gov.gst_number = gst_val if gst_val else None
                    gov.overall_status = 'UPLOADED'
                    gov.save()
                    
                    gst_val = onboarding_data.get('gst', '')
                    shop_val = onboarding_data.get('shop_name', '')
                    if gst_val or shop_val:
                        gst_model, _ = GSTModel.objects.get_or_create(user=user, defaults={'gst_number': None})
                        if gst_val: 
                            gst_model.gst_number = gst_val
                        else:
                            gst_model.gst_number = None
                        if shop_val: gst_model.business_name = shop_val
                        gst_model.save()
                        
                    address_val = onboarding_data.get('address', '')
                    if address_val or onboarding_data.get('pincode', ''):
                        addr_model, _ = AddressModel.objects.get_or_create(
                            user=user,
                            defaults={'panchayat': '','village': '','city': '','zilla': '','state': '','pincode': '','full_address': ''}
                        )
                        if address_val: addr_model.full_address = address_val
                        addr_model.pincode = onboarding_data.get('pincode', '')
                        addr_model.city = onboarding_data.get('city', '')
                        addr_model.zilla = onboarding_data.get('zilla', '')
                        addr_model.state = onboarding_data.get('state', '')
                        addr_model.save()
                        
                    acc_num = onboarding_data.get('account_number', '')
                    if acc_num or onboarding_data.get('ifsc_code', ''):
                        bank_model, _ = BankAccountModel.objects.get_or_create(user=user)
                        if acc_num: bank_model.account_number = acc_num
                        bank_model.ifsc_code = onboarding_data.get('ifsc_code', '')
                        bank_model.card_holder_name = onboarding_data.get('card_holder_name', '')
                        bank_model.save()
                        
                # Clear session
                request.session['onboarding_data'] = {}
                
                # Render an auto-submitting form to hit the login view, which will send OTP
                from django.urls import reverse
                login_url = reverse('login') + '?role=Seller'
                auto_submit_html = f"""
                <html>
                <body onload="document.getElementById('auto-login-form').submit();">
                    <form id="auto-login-form" method="POST" action="{login_url}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
                        <input type="hidden" name="mobile" value="{mobile}">
                    </form>
                    <p>Creating your account and sending OTP...</p>
                </body>
                </html>
                """
                from django.http import HttpResponse
                from django.middleware.csrf import get_token
                auto_submit_html = auto_submit_html.replace(
                    f'<input type="hidden" name="csrfmiddlewaretoken" value="{{request.META.get(\'CSRF_COOKIE\', \'\')}}">',
                    f'<input type="hidden" name="csrfmiddlewaretoken" value="{get_token(request)}">'
                )
                return HttpResponse(auto_submit_html)
                
        request.session['onboarding_data'] = onboarding_data
        next_step = step + 1
        return redirect('seller_onboarding_step', step=next_step)

class RoleSelectionView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'account/role_selection.html')

def role_aware_redirect(user):
    # Retrieve role if available
    role_name = user.roles.name if user.roles else 'Customer'
    
    if role_name == 'Seller':
        # Seller goes directly to upload wizard
        return redirect('upload_wizard')
    else:
        # Default to Customer
        return redirect('customer_home')

# ================================================== Language Preference Views ==================================================

class LanguagePreferenceView(BaseTemplateView):
    template_name= 'account/language_preference.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'languages': LanguagePreferenceModel.objects.all(),
            'cookie_form': CookieConsentForm()
        })
        return context
    
    def get(self, request, *args, **kwargs):
        print(getattr(request, 'data', 'No request.data attribute'))
        return self.render_to_response(self.get_context_data())
    
class LanguagePreferenceUpdateDashboardView(FormView):
    template_name = 'dashboard/language_preference_settings.html'
    form_class = LanguagePreferenceForm
    success_url = reverse_lazy('user_profile')

    def form_valid(self, form):
        language = form.cleaned_data['language']
        self.request.user.language_preference = language
        self.request.user.save()
        messages.success(self.request, "Language preference updated successfully.")
        response = super().form_valid(form)
        response.set_cookie('garuda_language', language.name, max_age=365*24*60*60)
        return response
    

class IndexComponentView(TemplateView):
    template_name = 'components/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add any context variables needed for the index.html template here
        return context

# Seller upload/redirect logic
class SellerUploadRedirectView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return redirect('upload_wizard')

# ======================================================= OTP Auth Views =======================================================

# ==================================================== Cart Views ====================================================



class CartView(CustomerRequiredMixin, TemplateView):
    template_name = 'costuner_flow/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        from decimal import Decimal, ROUND_HALF_UP
        from catalogue.models import ProductModel, ProductMediaModel
        subtotal = cart.subtotal() if hasattr(cart, 'subtotal') else Decimal('0.00')
        tax = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        context['cart'] = cart
        context['cart_tax'] = tax
        context['cart_total'] = total

        # Simplified recommendation logic for cart
        recommended = ProductModel.objects.filter(status='ACTIVE').order_by('?')[:4]
        recommended_with_media = []
        for product in recommended:
            media_objs = ProductMediaModel.objects.filter(product=product).order_by('display_order')
            recommended_with_media.append([product, media_objs])
        context['recommended_products'] = recommended_with_media

        return context
    

@method_decorator(csrf_exempt, name='dispatch')
class CartAddItemView(CustomerRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        if not product_id:
            return redirect('cart')
        product = get_object_or_404(ProductModel, pk=product_id)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()
        return redirect('cart')

@method_decorator(csrf_exempt, name='dispatch')
class CartUpdateQuantityView(CustomerRequiredMixin, View):
    def post(self, request, pk):
        from orders.models import CartItem, Cart  # Ensure CartItem and Cart are imported
        from decimal import Decimal, ROUND_HALF_UP
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        action = request.POST.get('action')
        if action == 'increase':
            item.quantity += 1
        elif action == 'decrease' and item.quantity > 1:
            item.quantity -= 1
        item.save()
        # AJAX support
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = item.cart
            cart_items = cart.items.all()
            subtotal = cart.subtotal() if hasattr(cart, 'subtotal') else Decimal('0.00')
            tax = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            
            items_total_mrp = sum((ci.product.price * ci.quantity) for ci in cart_items if ci.product.price)
            items_total_offer = sum(ci.total_price() for ci in cart_items)
            total_savings = items_total_mrp - items_total_offer

            return JsonResponse({
                'success': True,
                'quantity': item.quantity,
                'item_total': item.total_price(),
                'cart_subtotal': subtotal,
                'cart_tax': tax,
                'cart_total': total,
                'items_total_mrp': items_total_mrp,
                'items_total_offer': items_total_offer,
                'total_savings': total_savings,
            })
        
        return redirect('cart')

@method_decorator(csrf_exempt, name='dispatch')
class CartRemoveItemView(CustomerRequiredMixin, View):
    def post(self, request, pk):
        from orders.models import CartItem
        from decimal import Decimal, ROUND_HALF_UP
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart = item.cart
        item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            subtotal = cart.subtotal() if hasattr(cart, 'subtotal') else Decimal('0.00')
            tax = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return JsonResponse({
                'success': True,
                'cart_subtotal': subtotal,
                'cart_tax': tax,
                'cart_total': total,
            })
        return redirect('cart')
    def delete(self, request, pk):
        from orders.models import CartItem
        from decimal import Decimal, ROUND_HALF_UP
        item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
        cart = item.cart
        item.delete()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            subtotal = cart.subtotal() if hasattr(cart, 'subtotal') else Decimal('0.00')
            tax = (subtotal * Decimal('0.18')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            total = (subtotal + tax).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return JsonResponse({
                'success': True,
                'cart_subtotal': subtotal,
                'cart_tax': tax,
                'cart_total': total,
            })
        return redirect('cart')

class CheckoutSuccessView(CustomerRequiredMixin, TemplateView):
    template_name = 'costuner_flow/checkout_success.html'

class CheckoutAddressSelectionView(CustomerRequiredMixin, View):
    def get(self, request):
        addresses = request.user.customer_addresses.all().order_by('-is_default', '-id')
        return render(request, 'costuner_flow/checkout_address.html', {'addresses': addresses})

    def post(self, request):
        address_id = request.POST.get('address_id')
        if address_id:
            request.session['checkout_address_id'] = address_id
            return redirect('checkout_review')
        return redirect('checkout_address_selection')

class OrderReviewPlaceholderView(CustomerRequiredMixin, TemplateView):
    template_name = 'costuner_flow/checkout_review.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address_id = self.request.session.get('checkout_address_id')
        if address_id:
            from account.models import CustomerAddressModel
            address = CustomerAddressModel.objects.filter(id=address_id, user=self.request.user).first()
            context['selected_address'] = address
        
        # Get cart
        from orders.models import Cart
        cart = Cart.objects.filter(user=self.request.user).order_by('-created_at').first()
        if cart:
            context['cart'] = cart
            cart_items = cart.items.all()
            context['cart_items'] = cart_items
            
            from decimal import Decimal
            items_total_mrp = sum((item.product.price * item.quantity) for item in cart_items if item.product.price)
            
            # total_price() uses offer_price if available
            items_total_offer = sum(item.total_price() for item in cart_items)
            
            total_savings = items_total_mrp - items_total_offer
            
            context['items_total_mrp'] = items_total_mrp
            context['items_total_offer'] = items_total_offer
            context['total_savings'] = total_savings
            context['delivery_charges'] = Decimal('0.00')
            context['order_total'] = items_total_offer + context['delivery_charges']
            
            import datetime
            context['delivery_date'] = datetime.date.today() + datetime.timedelta(days=3)
            
        return context

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# ==================================================== Success Page Views ====================================================
class SuccessView(BaseTemplateView):
    template_name = 'success/success.html'    
    
# ==================================================== Dashboard Views ====================================================
class CustomerHomeView(CustomerRequiredMixin, TemplateView):

    template_name = 'costuner_flow/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from catalogue.models import CategoryModel, ProductModel, ProductMediaModel, Wishlist
        from django.db.models import Avg, Count, F
        
        user = self.request.user
        if user.is_authenticated:
            customer_addresses = user.customer_addresses.all()
            context['customer_addresses'] = customer_addresses
            context['user_address'] = customer_addresses.filter(is_default=True).first() or customer_addresses.first()
        else:
            context['customer_addresses'] = []
            context['user_address'] = None
        
        wishlist_product_ids = []
        if user.is_authenticated:
            wishlist_qs = Wishlist.objects.filter(user=user).first()
            if wishlist_qs:
                wishlist_product_ids = list(wishlist_qs.items.values_list('product_id', flat=True))
        context['wishlist_product_ids'] = wishlist_product_ids

        context['categories'] = CategoryModel.objects.filter(is_active=True)
        
        # Flash Sales: Active products with an offer price lower than original price
        flash_sales = ProductModel.objects.filter(
            status='ACTIVE', offer_price__lt=F('price'), offer_price__isnull=False
        ).order_by('-created_at')[:10]
        context['flash_sales'] = self._get_products_with_media(flash_sales)
        
        # New Arrivals: Latest active products
        new_arrivals = ProductModel.objects.filter(status='ACTIVE').order_by('-created_at')[:10]
        context['new_arrivals'] = self._get_products_with_media(new_arrivals)
        
        # Top Items: Based on views count and rating
        top_items = ProductModel.objects.filter(status='ACTIVE').annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        ).order_by('-views_count')[:10]
        context['top_items'] = self._get_products_with_media(top_items)

        return context

    def _get_products_with_media(self, products):
        from catalogue.models import ProductMediaModel
        products_with_media = []
        for product in products:
            media_objs = list(ProductMediaModel.objects.filter(product=product).order_by('display_order'))
            products_with_media.append([product, media_objs])
        return products_with_media

class CustomerProductSearchView(CustomerRequiredMixin, ListView):
    template_name = 'costuner_flow/search_results.html'
    context_object_name = 'products'

    def get_queryset(self):
        from catalogue.models import ProductModel
        from django.db.models import Q, Avg, Count, F
        queryset = ProductModel.objects.filter(status='ACTIVE')
        
        q = self.request.GET.get('q', '').strip()
        ids_str = self.request.GET.get('ids', '').strip()
        
        if ids_str:
            from django.db.models import Case, When
            id_list = [int(x) for x in ids_str.split(',') if x.isdigit()]
            if id_list:
                preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(id_list)])
                queryset = queryset.filter(id__in=id_list).order_by(preserved)
        elif q:
            queryset = queryset.filter(
                Q(name__icontains=q) | 
                Q(category__name__icontains=q) | 
                Q(description__icontains=q) |
                Q(tag_assignments__tag__name__icontains=q)
            ).distinct()
            
        category_ids = self.request.GET.getlist('category')
        if category_ids:
            queryset = queryset.filter(category__id__in=category_ids)
            
        price_range = self.request.GET.get('price_range')
        if price_range:
            if price_range == 'under_500':
                queryset = queryset.filter(price__lt=500)
            elif price_range == '500_1000':
                queryset = queryset.filter(price__gte=500, price__lt=1000)
            elif price_range == '1000_2000':
                queryset = queryset.filter(price__gte=1000, price__lt=2000)
            elif price_range == 'above_2000':
                queryset = queryset.filter(price__gte=2000)
                
        discount = self.request.GET.get('discount')
        if discount:
            try:
                discount_val = float(discount)
                factor = 1.0 - (discount_val / 100.0)
                queryset = queryset.filter(offer_price__isnull=False, offer_price__lte=F('price') * factor)
            except ValueError:
                pass
                
        queryset = queryset.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        
        rating = self.request.GET.get('rating')
        if rating:
            try:
                rating_val = int(rating)
                queryset = queryset.filter(avg_rating__gte=rating_val)
            except ValueError:
                pass
                
        sort = self.request.GET.get('sort')
        if sort:
            if sort == 'price_asc':
                queryset = queryset.order_by('price')
            elif sort == 'price_desc':
                queryset = queryset.order_by('-price')
            elif sort == 'rating_desc':
                queryset = queryset.order_by('-avg_rating')
            elif sort == 'newest':
                queryset = queryset.order_by('-created_at')
            elif sort == 'best_selling':
                queryset = queryset.order_by('-views_count')
                
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from catalogue.models import CategoryModel, Wishlist, ProductMediaModel
        user = self.request.user
        
        wishlist_product_ids = []
        if user.is_authenticated:
            wishlist_qs = Wishlist.objects.filter(user=user).first()
            if wishlist_qs:
                wishlist_product_ids = list(wishlist_qs.items.values_list('product_id', flat=True))
        context['wishlist_product_ids'] = wishlist_product_ids
        
        context['categories'] = CategoryModel.objects.filter(is_active=True)
        
        products_with_media = []
        for product in context['products']:
            media_objs = list(ProductMediaModel.objects.filter(product=product).order_by('display_order'))
            products_with_media.append([product, media_objs])
            
        context['products_with_media'] = products_with_media
        
        # Search History & Recommendation logic
        from account.models import SearchHistoryModel
        q = self.request.GET.get('q', '').strip()
        context['q'] = q
        
        if not q:
            # Empty search - fetch history
            if user.is_authenticated:
                context['search_history'] = SearchHistoryModel.objects.filter(user=user).order_by('-updated_at')
        else:
            # Always save search to history
            if user.is_authenticated:
                history, created = SearchHistoryModel.objects.get_or_create(user=user, query=q)
                if not created:
                    history.save() # Refresh updated_at
                    
            if not context['products']:
                # No results - fetch recommended products
                from catalogue.models import ProductModel
                # Simplified recommendation: just fetch some active products
                recommended = ProductModel.objects.filter(status='ACTIVE').order_by('?')[:4]
                recommended_with_media = []
                for product in recommended:
                    media_objs = list(ProductMediaModel.objects.filter(product=product).order_by('display_order'))
                    recommended_with_media.append([product, media_objs])
                context['recommended_products'] = recommended_with_media

        return context

class CustomerProductDetailView(CustomerRequiredMixin, TemplateView):
    template_name = 'costuner_flow/costumer_product_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(ProductModel, pk=product_id, status='ACTIVE')
        context['product'] = product
        
        # Product Images & Videos
        context['product_image_objects'] = product.media.exclude(image='').exclude(image__isnull=True).order_by('display_order')
        context['product_video_objects'] = product.media.exclude(video='').exclude(video__isnull=True).order_by('display_order')
        
        context['stock'] = getattr(product, 'stock_quantity', 0)
        
        # Delivery Address
        context['delivery_address'] = AddressModel.objects.filter(user=self.request.user).first()
        
        # Product Variants (Grouped by name)
        variants = ProductVariantModel.objects.filter(product=product)
        grouped_variants = {}
        for var in variants:
            if var.name not in grouped_variants:
                grouped_variants[var.name] = []
            grouped_variants[var.name].append(var)
        context['product_variants'] = grouped_variants
        
        # Reviews and Stats
        reviews = ProductReviewModel.objects.filter(product=product, is_approved=True).order_by('-created_at')
        total_reviews = reviews.count()
        context['reviews'] = reviews
        context['total_reviews'] = total_reviews
        
        review_stats = { 'avg': 0, 'counts': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}, 'percentages': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0} }
        if total_reviews > 0:
            total_score = 0
            for r in reviews:
                review_stats['counts'][r.rating] += 1
                total_score += r.rating
            review_stats['avg'] = round(total_score / total_reviews, 1)
            for star, count in review_stats['counts'].items():
                review_stats['percentages'][star] = int((count / total_reviews) * 100)
        context['review_stats'] = review_stats
        
        # Has Purchased (for Review button)
        context['has_purchased'] = OrderItemModel.objects.filter(order__user=self.request.user, product=product).exists()
        
        # Similar Products
        context['similar_products'] = ProductModel.objects.filter(category=product.category, status='ACTIVE').exclude(id=product.id)[:10]
        
        return context

    def post(self, request, *args, **kwargs):
        product_id = self.kwargs.get('pk')
        product = get_object_or_404(ProductModel, pk=product_id, status='ACTIVE')
        
        rating = int(request.POST.get('rating', 0))
        review_text = request.POST.get('review_text', '').strip()
        
        # Validate purchase
        has_purchased = OrderItemModel.objects.filter(order__user=request.user, product=product).exists()
        if not has_purchased:
            messages.error(request, "You can only review products you have purchased.")
            return redirect('customer_product_detail', pk=product_id)
            
        if rating < 1 or rating > 5:
            messages.error(request, "Please provide a valid rating.")
            return redirect('customer_product_detail', pk=product_id)
            
        ProductReviewModel.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            review_text=review_text,
            is_verified_purchase=True,
            is_approved=True
        )
        
        messages.success(request, "Review submitted successfully!")
        return redirect('customer_product_detail', pk=product_id)


class AccountDashboardView(BaseDashboardView):
    template_name = 'dashboard/account_settings.html'

class PrivacyPolicyDashboardView(BaseDashboardView):
    template_name = 'dashboard/privacy_policy.html'
    
class GarudAmbassadorView(BaseDashboardView):
    template_name = 'dashboard/garud_ambassador.html'
    
    def post(self, request, *args, **kwargs):
        # Handle POST requests gracefully. Redirect or add logic as needed.
        return self.get(request, *args, **kwargs)
    
class TermsAndConditionsView(BaseDashboardView):
    template_name = 'dashboard/terms_and_conditions.html'
    
    
class UserProfileDashboardView(BaseDashboardView):
    template_name = 'dashboard/user_profile_page.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, _ = UserProfileModel.objects.get_or_create(user=user)
        gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
        context.update({
            'user': user,
            'profile': profile,
            'gov_details': gov_details
        })
        return context

# ====================================================== Profile Update View ======================================================

class ProfileUpdateView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/profile_details.html'

    def get_user_related_models(self):
        user = self.request.user
        profile, _ = UserProfileModel.objects.get_or_create(user=user)
        govt_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
        gst_model, _ = GSTModel.objects.get_or_create(user=user)
        return user, profile, govt_details, gst_model
    
    def get_profile_forms(self, user, profile, govt_details, gst_model, data=None, files=None):
        return {
            'user_form': CustomUserForm(data, files, instance=user),
            'profile_form': UserProfileForm(data, instance=profile),
            'govt_form': GovernmentDetailsForm(data, instance=govt_details),
            'gst_form': GSTBusinessNameForm(data, instance=gst_model),
        }
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user, profile, govt_details, gst_model = self.get_user_related_models()
        forms = self.get_profile_forms(user, profile, govt_details, gst_model)
        context.update(forms)
        return context

    def post(self, request, *args, **kwargs):
        user, profile, govt_details, gst_model = self.get_user_related_models()
        forms = self.get_profile_forms(user, profile, govt_details, gst_model, request.POST, request.FILES)

        if all(form.is_valid() for form in forms.values()):
            if request.POST.get('remove_photo') == 'true' and user.photo:
                user.photo.delete(save=False)
            
            for form in forms.values():
                form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_profile')

        # Re-render the form with errors
        context = self.get_context_data()
        context.update(forms)
        return self.render_to_response(context)

# ======================================================= Address Update View =======================================================

# TODO: Make it like bank account where user can add multiple addresses add update and delete them
class AddressDashboardView(LoginRequiredMixin, UpdateView):
    model = AddressModel
    form_class = AddressForm
    template_name = 'dashboard/address_settings.html'
    success_url = reverse_lazy('user_profile')

    def get_object(self, queryset=None):
        address, created = AddressModel.objects.get_or_create(user=self.request.user)
        return address

    def form_valid(self, form):
        form.instance.user = self.request.user  
        messages.success(self.request, 'Address updated successfully!')
        return super().form_valid(form)

# ======================================================= Bank Account Views =======================================================

class AccountSettingsView(LoginRequiredMixin, UpdateView):
    model = BankAccountModel
    form_class = BankAccountForm
    template_name = 'dashboard/account_settings.html'
    success_url = reverse_lazy('account_settings')

    def get_object(self, queryset=None):
        account = BankAccountModel.objects.filter(user=self.request.user).first()
        return account

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Bank details updated successfully!')
        return super().form_valid(form)

class BankAccountUpdateView(LoginRequiredMixin, UpdateView):
    model = BankAccountModel
    form_class = BankAccountForm
    template_name = 'dashboard/account_add_edit.html'
    success_url = reverse_lazy('account_settings')

    def get_queryset(self):
        return BankAccountModel.objects.filter(user=self.request.user)
    
class BankAccountDeleteView(LoginRequiredMixin, DeleteView):
    model = BankAccountModel
    template_name = 'dashboard/account_delete.html'
    success_url = reverse_lazy('account_settings')

    def get_queryset(self):
        return BankAccountModel.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Bank account deleted successfully.")
        return super().delete(request, *args, **kwargs)



# ================================================== Address CRUD Views ==================================================
class AddressListView(LoginRequiredMixin, ListView):
    model = AddressModel
    template_name = 'dashboard/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = AddressModel
    form_class = AddressForm
    template_name = 'dashboard/address_add.html'
    success_url = reverse_lazy('address_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Address added successfully.")
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = AddressModel
    form_class = AddressForm
    template_name = 'dashboard/address_edit.html'
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Address updated successfully.")
        return super().form_valid(form)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = AddressModel
    template_name = 'dashboard/address_delete.html'
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return AddressModel.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Address deleted successfully.")
        return super().delete(request, *args, **kwargs)


@method_decorator(csrf_exempt, name='dispatch')
class AadhaarWebcamOCRView(View):
    template_name = 'seller/aadhaar_verification.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        try:
            # Check if JSON or Form Data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            option = data.get('option')
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})

            # Aadhaar scan via webcam images (GPT-4o vision, no OCR)
            if option == 'scan':
                front_img_data = None
                back_img_data = None

                if request.FILES.get('front_image') and request.FILES.get('back_image'):
                    import base64
                    front_file = request.FILES['front_image']
                    back_file = request.FILES['back_image']
                    front_img_data = f"data:{front_file.content_type};base64,{base64.b64encode(front_file.read()).decode()}"
                    back_img_data = f"data:{back_file.content_type};base64,{base64.b64encode(back_file.read()).decode()}"
                else:
                    front_img_data = data.get('front_image')
                    back_img_data = data.get('back_image')

                if not front_img_data or not back_img_data:
                    return JsonResponse({'success': False, 'error': 'No images sent'})
                load_dotenv()
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    return JsonResponse({'success': False, 'error': 'OpenAI API key not configured.'})
                # Prepare GPT-4o vision prompt
                content_list = [
                    {"type": "text", "text": "Carefully extract the following details from the image provided:- Full Name- Date of Birth (DOB) - Gender - Aadhaar Number - Full Address Make sure the Aadhaar number is exactly 12 digits. If any detail is unclear or missing, return `null` for that field.Respond in **strict JSON format** with these exact keys: name, dob, gender, aadhaar_number, address."},
                    {"type": "image_url", "image_url": {"url": front_img_data}},
                    {"type": "image_url", "image_url": {"url": back_img_data}}
                ]
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": content_list}],
                    max_tokens=500,
                )
                json_text = response.choices[0].message.content
                try:
                    # Remove triple backticks and optional 'json' label
                    cleaned = json_text.strip()
                    if cleaned.startswith('```'):
                        cleaned = cleaned.lstrip('`')
                        # Remove 'json' label if present
                        if cleaned.lower().startswith('json'):
                            cleaned = cleaned[4:].strip()
                        # Remove trailing backticks
                        if cleaned.endswith('```'):
                            cleaned = cleaned[:-3].strip()
                    parsed_data = json.loads(cleaned)
                    
                    # Sanitize Aadhaar number
                    aadhaar_str = str(parsed_data.get('aadhaar_number', ''))
                    import re
                    aadhaar_clean = re.sub(r'\D', '', aadhaar_str)
                    if len(aadhaar_clean) != 12:
                        return JsonResponse({'success': False, 'error': 'Could not extract a valid 12-digit Aadhaar number.'})
                    parsed_data['aadhaar_number'] = aadhaar_clean
                    
                except Exception as e:
                    print("GPT-4o extraction error")
                    return JsonResponse({'success': False, 'error': 'AI extraction failed.'})
                gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                gov_details.aadhar_card_number = parsed_data.get('aadhaar_number')
                gov_details.aadhar_front_image.save("front.jpg", ContentFile(base64.b64decode(front_img_data.split(',')[-1])), save=False)
                gov_details.aadhar_back_image.save('back.jpg', ContentFile(base64.b64decode(back_img_data.split(',')[-1])), save=False)
                gov_details.aadhaar_status = 'VERIFIED'
                gov_details.save()
                return JsonResponse({'success': True, 'data': parsed_data})

            # Manual Aadhaar entry
            elif option == 'manual':
                aadhar_card_number = data.get('aadhaar_number')
                if not aadhar_card_number or len(aadhar_card_number) != 12 or not aadhar_card_number.isdigit():
                    return JsonResponse({'success': False, 'error': 'Invalid Aadhaar number format'})
                
                # Check for duplicate
                if GovernmentDetailsModel.objects.exclude(user=user).filter(aadhar_card_number=aadhar_card_number).exists():
                    return JsonResponse({'success': False, 'error': 'This Aadhaar number is already registered to another account.'})

                gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=user)
                gov_details.aadhar_card_number = aadhar_card_number
                gov_details.aadhaar_status = 'VERIFIED'
                gov_details.save()
                return JsonResponse({'success': True})

            # Mobile number entry
            elif option == 'mobile':
                mobile = data.get('mobile')
                if not mobile or len(mobile) != 10 or not mobile.isdigit():
                    return JsonResponse({'success': False, 'error': 'Invalid mobile number format'})
                gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
                # Optionally save mobile number if model supports it
                gov_details.aadhaar_status = 'VERIFIED'
                gov_details.save()
                return JsonResponse({'success': True})

            return JsonResponse({'success': False, 'error': 'Invalid option'})
        except Exception as e:
            import traceback
            print(f"Error in AadhaarWebcamOCRView: {e}")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': 'Server error occurred. Check backend logs for details.'})
        
@method_decorator(csrf_exempt, name='dispatch')
class SubmitManualAadhaarView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            aadhaar = data.get("aadhaar_number")
            
            if not aadhaar or len(aadhaar) != 12 or not aadhaar.isdigit():
                return JsonResponse({"success": False, "error": "Invalid Aadhaar number format"})
            
            user = request.user
            # Check for duplicate
            if GovernmentDetailsModel.objects.exclude(user=user).filter(aadhar_card_number=aadhaar).exists():
                return JsonResponse({'success': False, 'error': 'This Aadhaar number is already registered to another account.'})

            # Save Aadhaar to database
            gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=user)
            gov_details.aadhar_card_number = aadhaar
            gov_details.aadhaar_status = 'VERIFIED'
            gov_details.save()
            
            print(f"Manual Aadhaar saved: {aadhaar} for user: {user.mobile}")
            return JsonResponse({"success": True})
            
        except Exception as e:
            print(f"Error saving manual Aadhaar: {e}")
            return JsonResponse({"success": False, "error": "Failed to save Aadhaar"})

@method_decorator(csrf_exempt, name='dispatch')
class SubmitMobileView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            mobile = data.get("mobile")
            
            if not mobile or len(mobile) != 10 or not mobile.isdigit():
                return JsonResponse({"success": False, "error": "Invalid mobile number format"})
            
            # Save mobile to database - you might want to add a mobile field to GovernmentDetailsModel
            # For now, we'll just create/update the record to show the user exists
            user = request.user
            gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=user)
            gov_details.aadhaar_status = 'VERIFIED'
            # Note: Add a mobile_number field to GovernmentDetailsModel if you want to store this
            gov_details.save()
            
            print(f"Mobile number processed: {mobile} for user: {user.mobile}")
            return JsonResponse({"success": True})
            
        except Exception as e:
            print(f"Error processing mobile: {e}")
            return JsonResponse({"success": False, "error": "Failed to process mobile number"})
    


class AadhaarSubmitView(SellerRequiredMixin, FormView):
    template_name = 'seller/aadhaar_verification.html'
    form_class = AadhaarForm
    success_url = reverse_lazy('verification_progress')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create the government details instance for the form
        gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=self.request.user)
        kwargs['instance'] = gov_details
        print(f"AadhaarSubmitView: get_form_kwargs - Gov details ID: {gov_details.id}, created: {created}")
        return kwargs

    def form_valid(self, form):
        try:
            print(f"AadhaarSubmitView: Processing form for user: {self.request.user.mobile}")
            print(f"Form data: {form.cleaned_data}")
            
            # Save the form instance with the user
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()

            print(f"Aadhaar saved: {instance.aadhar_card_number} for user: {self.request.user.mobile}")

            # Verify it was saved
            saved_gov_details = GovernmentDetailsModel.objects.get(user=self.request.user)
            print(f"Verification - Saved Aadhaar: {saved_gov_details.aadhar_card_number}")
            saved_gov_details.aadhaar_status = 'VERIFIED'
            saved_gov_details.save()
            
            return super().form_valid(form)
        except Exception as e:
            print(f"Error saving Aadhaar: {e}")
            return self.form_invalid(form)

class SuccessView(TemplateView):
    template_name = 'success/success.html'

class OnboardingSuccessView(SellerRequiredMixin, TemplateView):
    template_name = 'seller/onboarding_success.html'

class AnnualIncomeView(SellerRequiredMixin, FormView):
    template_name = 'seller/annual_income.html'
    form_class = AnnualIncomeForm
    success_url = reverse_lazy('verification_progress')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create with default values for required fields
        profile, created = UserProfileModel.objects.get_or_create(
            user=self.request.user,
            defaults={
                'full_name': 'Unknown',  # Default value for required field
                'gender': 'M',  # Default value for required field
                'date_of_birth': date(2000, 1, 1),  # Default date object
                'annual_income': 0,
                'occupation': 'Unknown'
            }
        )
        kwargs['instance'] = profile
        return kwargs

    def form_valid(self, form):
        try:
            print(f"AnnualIncomeView: Processing form for user: {self.request.user.mobile}")
            print(f"Form data: {form.cleaned_data}")
            
            # Save the form instance with the user
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()

            print(f"Annual income saved: {instance.annual_income} for user: {self.request.user.mobile}")

            # Verify it was saved
            saved_profile = UserProfileModel.objects.get(user=self.request.user)
            print(f'Verification - Saved annual income: {saved_profile.annual_income}')
            
            gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=self.request.user)
            gov_details.income_status = 'VERIFIED'
            gov_details.save()
            
            return super().form_valid(form)
        except Exception as e:
            print(f"Error saving annual income: {e}")
            import traceback
            traceback.print_exc()
            return self.form_invalid(form)

class OccupationView(SellerRequiredMixin, FormView):
    template_name = 'seller/occupation.html'
    form_class = OccupationForm
    success_url = reverse_lazy('verification_progress')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create the user profile instance for the form
        profile, created = UserProfileModel.objects.get_or_create(
            user=self.request.user,
            defaults={
                'full_name': 'Unknown',  # Default value for required field
                'gender': 'M',  # Default value for required field
                'date_of_birth': date(2000, 1, 1),  # Default date object
                'annual_income': 0,
                'occupation': 'Unknown'
            }
        )
        kwargs['instance'] = profile
        print(f"OccupationView: get_form_kwargs - Profile ID: {profile.id}, created: {created}")
        return kwargs

    def form_valid(self, form):
        try:
            print(f"OccupationView: Processing form for user: {self.request.user.mobile}")
            print(f"Form data: {form.cleaned_data}")

            # Save the form instance with the user
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()
            
            print(f"Occupation saved: {instance.occupation} for user: {self.request.user.mobile}")
            
            # Verify it was saved
            saved_profile = UserProfileModel.objects.get(user=self.request.user)
            print(f"Verification - Saved occupation: {saved_profile.occupation}")
            
            gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=self.request.user)
            gov_details.occupation_status = 'VERIFIED'
            gov_details.save()
            
            return super().form_valid(form)
        except Exception as e:
            print(f"Error saving occupation: {e}")
            import traceback
            traceback.print_exc()
            return self.form_invalid(form)

class GSTNumberView(SellerRequiredMixin, FormView):
    template_name = 'seller/gst_number.html'
    form_class = GSTNumberForm
    success_url = reverse_lazy('verification_progress')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create the government details instance for the form
        gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=self.request.user)
        kwargs['instance'] = gov_details
        print(f"GSTNumberView: get_form_kwargs - Gov details ID: {gov_details.id}, created: {created}")
        return kwargs

    def form_valid(self, form):
        try:
            print(f"GSTNumberView: Processing form for user: {self.request.user.mobile}")
            print(f"Form data: {form.cleaned_data}")
            
            # Save the form instance with the user
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.save()

            print(f"GST number saved: {instance.gst_number} for user: {self.request.user.mobile}")

            # Verify it was saved
            saved_gov = GovernmentDetailsModel.objects.get(user=self.request.user)
            print(f'Verification - Saved GST: {saved_gov.gst_number}')
            saved_gov.gst_status = 'VERIFIED'
            saved_gov.save()
            return super().form_valid(form)
        except Exception as e:
            print(f"Error saving GST number: {e}")
            import traceback
            traceback.print_exc()
            return self.form_invalid(form)

class PANCardView(SellerRequiredMixin, FormView):
    template_name = 'seller/pan_card.html'
    form_class = PANCardForm
    success_url = reverse_lazy('verification_progress')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Get or create the government details instance for the form
        gov_details, created = GovernmentDetailsModel.objects.get_or_create(user=self.request.user)
        kwargs['instance'] = gov_details
        print(f"PANCardView: get_form_kwargs - Gov details ID: {gov_details.id}, created: {created}")
        return kwargs

    def post(self, request, *args, **kwargs):
        # Handle AJAX requests for PAN card scanning
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return self.handle_ajax_request(request)
        
        # Handle regular form submission for manual PAN entry
        return super().post(request, *args, **kwargs)

    def handle_ajax_request(self, request):
        try:
            user = request.user
            if not user.is_authenticated:
                return JsonResponse({'success': False, 'error': 'User not authenticated'})

            # Check if it's a scan request (with front image) or manual entry
            if 'front_image' in request.POST:
                return self.handle_scan_request(request, user)
            elif 'pan_card_number' in request.POST:
                return self.handle_manual_request(request, user)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid request data'})

        except Exception as e:
            print(f"Error in PANCardView AJAX: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': 'Server error occurred'})

    def handle_scan_request(self, request, user):
        try:
            front_img = request.POST.get('front_image')
            if not front_img:
                return JsonResponse({'success': False, 'error': 'No image provided'})
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return JsonResponse({'success': False, 'error': 'OpenAI API key not configured.'})
            # Prepare GPT-4o vision prompt
            content_list = [
                {"type": "text", "text": "Carefully extract the following details from the image provided: - PAN Number (format: XXXXX9999X - 5 letters, 4 digits, 1 letter) - Full Name - Father's Name - Date of Birth (DOB) - Signature (if visible, just say 'Present' or 'Not visible'). Respond in strict JSON format with these exact keys: pan_number, name, father_name, dob, signature. If any detail is unclear or missing, return null for that field."},
                {"type": "image_url", "image_url": {"url": front_img}}
            ]
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": content_list}],
                max_tokens=500,
            )
            json_text = response.choices[0].message.content.strip()
            # Clean JSON response (remove markdown formatting if present)
            if json_text.startswith('```json'):
                json_text = json_text.replace('```json', '').replace('```', '').strip()
            elif json_text.startswith('```'):
                json_text = json_text.replace('```', '').strip()
            try:
                parsed_data = json.loads(json_text)
            except Exception as e:
                print("GPT-4o response not valid JSON:", json_text)
                return JsonResponse({'success': False, 'error': 'AI extraction failed.'})
            gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
            gov_details.pan_card_number = parsed_data.get('pan_number')
            from django.core.files.base import ContentFile
            gov_details.pan_front_image.save("pan_front.jpg", ContentFile(base64.b64decode(front_img.split(',')[-1])), save=False)
            gov_details.pan_status = 'VERIFIED'
            gov_details.save()
            print(f"PAN scan saved: {parsed_data.get('pan_number')} for user: {user.mobile}")
            return JsonResponse({'success': True, 'data': parsed_data})
        except Exception as e:
            print(f"Error in PAN scan processing: {e}")
            traceback.print_exc()
            return JsonResponse({'success': False, 'error': 'Failed to process PAN card image'})

    def handle_manual_request(self, request, user):
        try:
            pan_number = request.POST.get('pan_card_number', '').strip().upper()
            if not pan_number:
                return JsonResponse({'success': False, 'error': 'PAN card number is required'})
            pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
            if not re.match(pan_regex, pan_number):
                return JsonResponse({'success': False, 'error': 'Invalid PAN card format'})
            gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
            gov_details.pan_card_number = pan_number
            gov_details.pan_status = 'VERIFIED'
            gov_details.save()
            print(f"Manual PAN saved: {pan_number} for user: {user.mobile}")
            # Return PAN details for frontend display
            return JsonResponse({'success': True, 'data': {
                'pan_number': pan_number,
                'name': 'Not found',
                'father_name': 'Not found',
                'dob': 'Not found',
                'signature': 'Not found'
            }})
        except Exception as e:
            print(f"Error in manual PAN processing: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to save PAN card number'})

    def extract_pan_details_with_ai(self, extracted_text):
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key:
                print("OpenAI API key not found")
                return None

            prompt = f"""
                        Extract the following details from the PAN card OCR text below. The text might be noisy or incomplete due to OCR errors:

                        - PAN Number (format: XXXXX9999X - 5 letters, 4 digits, 1 letter)
                        - Full Name
                        - Father's Name
                        - Date of Birth (DOB)
                        - Signature (if visible, just say "Present" or "Not visible")

                        OCR Text:
                        {extracted_text}

                        Instructions:
                        1. Look for patterns that match PAN number format even if there are OCR errors
                        2. Extract names even if they are partially readable
                        3. If exact information is not found, use "Not found" as the value
                        4. Be tolerant of OCR errors and try to infer correct values

                        Respond in JSON format with keys: pan_number, name, father_name, dob, signature.
                        Example: {{"pan_number": "ABCDE1234F", "name": "JOHN DOE", "father_name": "ROBERT DOE", "dob": "01/01/1990", "signature": "Present"}}
                    """

            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1  # Lower temperature for more consistent results
            )
            
            json_text = response.choices[0].message.content.strip()
            print(f"OpenAI response: {json_text}")
            
            # Clean JSON response (remove markdown formatting if present)
            if json_text.startswith('```json'):
                json_text = json_text.replace('```json', '').replace('```', '').strip()
            elif json_text.startswith('```'):
                json_text = json_text.replace('```', '').strip()
            
            # Try to extract JSON from the response
            try:
                parsed_data = json.loads(json_text)
                
                # Validate PAN number format if found
                pan_number = parsed_data.get('pan_number', '')
                if pan_number and pan_number != 'Not found':
                    # Clean and validate PAN number
                    pan_number = re.sub(r'[^A-Z0-9]', '', pan_number.upper())
                    if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
                        parsed_data['pan_number'] = pan_number
                    else:
                        # Try to find PAN pattern in the text
                        pan_matches = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', extracted_text.upper())
                        if pan_matches:
                            parsed_data['pan_number'] = pan_matches[0]
                
                return parsed_data
                
            except json.JSONDecodeError as je:
                print(f"JSON decode error: {je}")
                print(f"Response text: {json_text}")
                return None

        except Exception as e:
            print(f"Error in AI processing: {e}")
            traceback.print_exc()
            return None

    def form_valid(self, form):
        try:
            print(f"PANCardView: Processing form for user: {self.request.user.mobile}")
            print(f"Form data: {form.cleaned_data}")
            
            # Save the form instance with the user
            instance = form.save(commit=False)
            instance.user = self.request.user
            instance.pan_status = 'VERIFIED'
            instance.save()

            print(f"PAN number saved: {instance.pan_card_number} for user: {self.request.user.mobile}")

            # Verify it was saved
            saved_gov = GovernmentDetailsModel.objects.get(user=self.request.user)
            print(f"Verification - Saved PAN: {saved_gov.pan_card_number}")
            
            return super().form_valid(form)
        except Exception as e:
            print(f"Error saving PAN number: {e}")
            import traceback
            traceback.print_exc()
            return self.form_invalid(form)

# ==================================================== Phone Number Confirmation View ====================================================

class PhoneConfirmationView(SellerRequiredMixin, FormView,):
    template_name = 'seller/phone_confirmation.html'
    form_class = PhoneConfirmationForm
    success_url = reverse_lazy('verification_progress')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_phone'] = self.request.user.mobile
        return context

    def form_valid(self, form):
        action = form.cleaned_data['action']
        
        if action == 'continue':
            # User wants to continue with current phone number
            return super().form_valid(form)
        
        elif action == 'change':
            # User wants to change phone number
            new_phone_number = form.cleaned_data['new_phone_number']
            
            try:
                # Store current user's data before switching
                current_user = self.request.user
                
                # Check if a user with the new phone number already exists
                existing_user = User.objects.filter(phone_number=new_phone_number).first()
                
                if existing_user:
                    # If user exists, log them in and continue
                    logout(self.request)
                    login(self.request, existing_user)
                    print(f"Switched to existing user: {new_phone_number}")
                else:
                    # Update the current user's phone number instead of creating new user
                    current_user.phone_number = new_phone_number
                    current_user.save()
                    print(f"Updated phone number to: {new_phone_number} for user ID: {current_user.id}")
                return super().form_valid(form)
                
            except Exception as e:
                print(f"Error handling phone number change: {e}")
                form.add_error('new_phone_number', 'Error processing phone number change. Please try again.')
                return self.form_invalid(form)


#             print(f"Error processing mobile: {e}")
#             return JsonResponse({'success': False, 'error': 'Failed to process mobile number'})
    
#     def handle_pan_ocr(self, request):
#         """Handle PAN card OCR processing from form data"""
#         try:
#             user = request.user
#             if not user.is_authenticated:
#                 return JsonResponse({'success': False, 'error': 'User not authenticated'})

#             # Check if it's a scan request or manual entry
#             if 'front_image' in request.POST:
#                 return self._process_pan_scan(request, user)
#             elif 'pan_card_number' in request.POST:
#                 return self._process_pan_manual(request, user)
#             else:
#                 return JsonResponse({'success': False, 'error': 'Invalid request data'})

#         except Exception as e:
#             print(f"Error in PAN OCR: {e}")
#             return JsonResponse({'success': False, 'error': 'Server error occurred'})
    
#     def _process_pan_scan(self, request, user):
#         """Process PAN card scan with OCR"""
#         try:
#             front_img = request.POST.get('front_image')
            
#             if not front_img:
#                 return JsonResponse({'success': False, 'error': 'No image provided'})

#             # Extract text from the front image using OCR
#             extracted_text = self._extract_text_from_pan_image(front_img)
            
#             if not extracted_text.strip():
#                 return JsonResponse({'success': False, 'error': 'Could not extract readable text from image'})

#             # Use OpenAI to parse PAN card details
#             parsed_data = self._extract_pan_details_with_ai(extracted_text)
            
#             if not parsed_data:
#                 # Fallback to regex extraction
#                 pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]{1}'
#                 pan_matches = re.findall(pan_pattern, extracted_text.upper())
                
#                 if pan_matches:
#                     parsed_data = {
#                         'pan_number': pan_matches[0],
#                         'name': 'Extracted from OCR',
#                         'father_name': 'Not found',
#                         'dob': 'Not found',
#                         'signature': 'Not found'
#                     }
#                 else:
#                     return JsonResponse({'success': False, 'error': 'Could not parse PAN card details'})

#             # Save to database
#             gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
#             gov_details.pan_card_number = parsed_data.get('pan_number')
#             gov_details.pan_front_image.save("pan_front.jpg", ContentFile(base64.b64decode(front_img.split(',')[-1])), save=False)
#             gov_details.save()
            
#             print(f"PAN scan saved: {parsed_data.get('pan_number')} for user: {user.phone_number}")
            
#             return JsonResponse({'success': True, 'data': parsed_data})

#         except Exception as e:
#             print(f"Error in PAN scan: {e}")
#             return JsonResponse({'success': False, 'error': 'Failed to process PAN card image'})
    
#     def _process_pan_manual(self, request, user):
#         """Process manual PAN entry"""
#         try:
#             pan_number = request.POST.get('pan_card_number', '').strip().upper()
            
#             if not pan_number:
#                 return JsonResponse({'success': False, 'error': 'PAN card number is required'})
            
#             # Validate PAN format
#             pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
#             if not re.match(pan_regex, pan_number):
#                 return JsonResponse({'success': False, 'error': 'Invalid PAN card format'})
            
#             # Save to database
#             gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
#             gov_details.pan_card_number = pan_number
#             gov_details.save()
            
#             print(f"Manual PAN saved: {pan_number} for user: {user.phone_number}")
#             return JsonResponse({'success': True})

#         except Exception as e:
#             print(f"Error in manual PAN: {e}")
#             return JsonResponse({'success': False, 'error': 'Failed to save PAN card number'})
    
#     def handle_step_submission(self, request, step):
#         """Handle form submission for specific steps"""
#         user = request.user
        
#         try:
#             if step == '1':
#                 return self.handle_phone_confirmation(request, user)
#             elif step == '2':
#                 return self.handle_aadhaar_submission(request, user)
#             elif step == '3':
#                 return self.handle_income_submission(request, user)
#             elif step == '4':
#                 return self.handle_occupation_submission(request, user)
#             elif step == '5':
#                 return self.handle_gst_submission(request, user)
#             elif step == '6':
#                 return self.handle_pan_submission(request, user)
#             else:
#                 return self._error_response('Invalid step')
                
#         except Exception as e:
#             print(f"Error handling step {step}: {e}")
#             return self._error_response(f'Error processing step {step}')
    
#     def handle_phone_confirmation(self, request, user):
#         """Handle phone confirmation step"""
#         form = PhoneConfirmationForm(request.POST)
#         if form.is_valid():
#             action = form.cleaned_data['action']
#             if action == 'continue':
#                 return self._success_response('Phone number confirmed', next_step=2)
#             elif action == 'change':
#                 new_phone = form.cleaned_data['new_phone_number']
#                 try:
#                     self._handle_phone_change(request, user, new_phone)
#                     return self._success_response('Phone number changed successfully', next_step=2)
#                 except Exception as e:
#                     return self._error_response('Error changing phone number')
#         return self._form_error_response(form, 1)
    
#     def handle_aadhaar_submission(self, request, user):
#         """Handle Aadhaar verification step"""
#         gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
#         form = AadhaarForm(request.POST, request.FILES, instance=gov_details)
#         if form.is_valid():
#             form.save()
#             return self._success_response('Aadhaar details saved successfully', next_step=3)
#         return self._form_error_response(form, 2)
    
#     def handle_income_submission(self, request, user):
#         """Handle annual income step"""
#         profile, _ = UserProfileModel.objects.get_or_create(
#             user=user,
#             defaults={
#                 'full_name': 'Unknown',
#                 'gender': 'M',
#                 'date_of_birth': date(2000, 1, 1),
#                 'annual_income': 0,
#                 'occupation': 'Unknown'
#             }
#         )
#         form = AnnualIncomeForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return self._success_response('Annual income saved successfully', next_step=4)
#         return self._form_error_response(form, 3)
    
#     def handle_occupation_submission(self, request, user):
#         """Handle occupation step"""
#         profile, _ = UserProfileModel.objects.get_or_create(
#             user=user,
#             defaults={
#                 'full_name': 'Unknown',
#                 'gender': 'M',
#                 'date_of_birth': date(2000, 1, 1),
#                 'annual_income': 0,
#                 'occupation': 'Unknown'
#             }
#         )
#         form = OccupationForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return self._success_response('Occupation saved successfully', next_step=5)
#         return self._form_error_response(form, 4)
    
#     def handle_gst_submission(self, request, user):
#         """Handle GST number step"""
#         gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
#         form = GSTNumberForm(request.POST, instance=gov_details)
#         if form.is_valid():
#             form.save()
#             return self._success_response('GST details saved successfully', next_step=6)
#         return self._form_error_response(form, 5)
    
#     def handle_pan_submission(self, request, user):
#         """Handle PAN card step"""
#         gov_details, _ = GovernmentDetailsModel.objects.get_or_create(user=user)
#         form = PANCardForm(request.POST, instance=gov_details)
#         if form.is_valid():
#             form.save()
#             return self._success_response('KYC process completed successfully!', redirect_url='/user-profile/')
#         return self._form_error_response(form, 6)
    
#     # Helper methods for AI processing
#     def _extract_aadhaar_details_with_ai(self, extracted_text):
#         """Extract Aadhaar details using OpenAI"""
#         try:
#             load_dotenv()
#             api_key = os.getenv("OPENAI_API_KEY")
#             if not api_key:
#                 return None

#             prompt = f"""
# Extract the following details from the Aadhaar OCR text below:
# - Full Name
# - Date of Birth (DOB)
# - Gender
# - Aadhaar Number
# - Address

# OCR Text:
# {extracted_text}

# Respond in JSON with keys: name, dob, gender, aadhaar_number, address.
#             """

#             client = OpenAI(api_key=api_key)
#             response = client.chat.completions.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.2
#             )
#             json_text = response.choices[0].message.content
#             return json.loads(json_text)
            
#         except Exception as e:
#             print(f"Error in Aadhaar AI processing: {e}")
#             return None
    
#     def _extract_text_from_pan_image(self, front_img):
#         """Extract text from PAN card image using OCR"""
#         try:
#             img_data = base64.b64decode(front_img.split(',')[-1])
#             with tempfile.NamedTemporaryFile(suffix='.jpg', delete=True) as temp_image:
#                 temp_image.write(img_data)
#                 temp_image.flush()
#                 image = cv2.imread(temp_image.name)
                
#                 if image is not None:
#                     extracted_texts = []
                    
#                     # Basic preprocessing
#                     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#                     text1 = pytesseract.image_to_string(gray, lang='eng', config='--psm 6')
#                     if text1.strip():
#                         extracted_texts.append(text1)
                    
#                     # Enhanced preprocessing
#                     denoised = cv2.medianBlur(gray, 5)
#                     _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#                     scale_percent = 300
#                     width = int(thresh.shape[1] * scale_percent / 100)
#                     height = int(thresh.shape[0] * scale_percent / 100)
#                     dim = (width, height)
#                     resized = cv2.resize(thresh, dim, interpolation=cv2.INTER_CUBIC)
#                     text2 = pytesseract.image_to_string(resized, lang='eng')
#                     if text2.strip():
#                         extracted_texts.append(text2)
                    
#                     return '\n'.join(extracted_texts)
#             return ""
            
#         except Exception as e:
#             print(f"Error extracting text from PAN image: {e}")
#             return ""
    
#     def _extract_pan_details_with_ai(self, extracted_text):
#         """Extract PAN details using OpenAI"""
#         try:
#             load_dotenv()
#             api_key = os.getenv("OPENAI_API_KEY")
#             if not api_key:
#                 return None

#             prompt = f"""
# Extract the following details from the PAN card OCR text below:
# - PAN Number (format: XXXXX9999X - 5 letters, 4 digits, 1 letter)
# - Full Name
# - Father's Name
# - Date of Birth (DOB)
# - Signature (if visible, just say "Present" or "Not visible")

# OCR Text:
# {extracted_text}

# Respond in JSON format with keys: pan_number, name, father_name, dob, signature.
#             """

#             client = OpenAI(api_key=api_key)
#             response = client.chat.completions.create(
#                 model="gpt-4",
#                 messages=[{"role": "user", "content": prompt}],
#                 temperature=0.1
#             )
            
#             json_text = response.choices[0].message.content.strip()
            
#             # Clean JSON response
#             if json_text.startswith('```json'):
#                 json_text = json_text.replace('```json', '').replace('```', '').strip()
#             elif json_text.startswith('```'):
#                 json_text = json_text.replace('```', '').strip()
            
#             parsed_data = json.loads(json_text)
            
#             # Validate PAN number
#             pan_number = parsed_data.get('pan_number', '')
#             if pan_number and pan_number != 'Not found':
#                 pan_number = re.sub(r'[^A-Z0-9]', '', pan_number.upper())
#                 if re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_number):
#                     parsed_data['pan_number'] = pan_number
#                 else:
#                     pan_matches = re.findall(r'[A-Z]{5}[0-9]{4}[A-Z]{1}', extracted_text.upper())
#                     if pan_matches:
#                         parsed_data['pan_number'] = pan_matches[0]
            
#             return parsed_data
            
#         except Exception as e:
#             print(f"Error in PAN AI processing: {e}")
#             return None

#     def _handle_phone_change(self, request, current_user, new_phone):
#         """Handle phone number change logic"""
#         try:
#             existing_user = User.objects.filter(phone_number=new_phone).first()
            
#             if existing_user:
#                 # Switch to existing user
#                 logout(request)
#                 login(request, existing_user)
#                 print(f"Switched to existing user: {new_phone}")
#             else:
#                 # Update current user's phone number
#                 current_user.phone_number = new_phone
#                 current_user.save()
#                 print(f"Updated phone number to: {new_phone}")
                
#         except Exception as e:
#             print(f"Error handling phone change: {e}")
#             raise e
    
#     # Response helper methods
#     def _success_response(self, message, next_step=None, redirect_url=None):
#         """Generate success response"""
#         response_data = {'success': True, 'message': message}
#         if next_step:
#             response_data['next_step'] = next_step
#         if redirect_url:
#             response_data['redirect_url'] = redirect_url
#         return JsonResponse(response_data)
    
#     def _error_response(self, message):
#         """Generate error response"""
#         return JsonResponse({'success': False, 'error': message})
    
#     def _form_error_response(self, form, step):
#         """Generate form error response"""
#         errors = {}
#         for field, error_list in form.errors.items():
#             errors[field] = error_list[0] if error_list else 'Invalid value'
        
#         return JsonResponse({
#             'success': False,
#             'error': 'Form validation failed',
#             'form_errors': errors,
#             'step': step      
#         })




@method_decorator(csrf_exempt, name='dispatch')
class ProductUploadWizardView(SellerRequiredMixin, View):
    """Multi-step product upload wizard with AI integration"""
    
    def get(self, request):
        """Load the stepper UI"""
        if not request.user.is_authenticated:
            return redirect('login')
            
        step = int(request.GET.get('step', 1))
        # Initialize session data if needed
        if 'product_upload_data' not in request.session:
            request.session['product_upload_data'] = {
                'step': 1,
                'images': [],
                'videos': [],
                'product_data': {}
            }
        context = {
            'current_step': step,
            'categories': CategoryModel.objects.filter(is_active=True),
            'upload_data': request.session.get('product_upload_data', {})
        }
        return render(request, 'product_listing/upload_wizard.html', context)
    
    def post(self, request):
        """Handle AJAX requests for each step"""
        try:
            step = int(request.POST.get('step', 1))
            
            if step == 1:
                return self._handle_media_upload(request)
            elif step == 2:
                return self._handle_ai_name_generation(request)
            elif step == 3:
                return self._handle_ai_description_generation(request)
            elif step == 4:
                return self._handle_ai_category_generation(request)
            elif step == 5:
                return self._handle_ai_price_generation(request)
            elif step == 6:
                return self._handle_quantity_input(request)
            elif step == 7:
                return self._handle_final_submission(request)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid step'})
                
        except Exception as e:
            print(f"Error in ProductUploadWizardView: {e}")
            return JsonResponse({'success': False, 'error': 'Server error occurred'})
    
    def _handle_media_upload(self, request):
        """Step 1: Handle media upload and generate ALL AI content at once"""
        try:
            images_base64 = request.POST.getlist('images')
            videos_base64 = request.POST.getlist('videos')
            
            if not images_base64 and not videos_base64:
                return JsonResponse({'success': False, 'error': 'At least one image or video is required'})
            
            # Generate all AI content at once after media upload
            ai_content = self._generate_all_ai_content(images_base64)
            
            if not ai_content['success']:
                return JsonResponse({'success': False, 'error': ai_content['error']})
            
            # Store everything in session
            request.session['product_upload_data'] = {
                'step': 2,
                'images': images_base64,
                'videos': videos_base64,
                'product_data': ai_content['data']
            }
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Media uploaded and AI content generated successfully',
                'next_step': 2,
                'media_count': len(images_base64) + len(videos_base64),
                'ai_content': ai_content['data']
            })
            
        except Exception as e:
            print(f"Error in media upload: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to upload media'})
    
    def _handle_ai_name_generation(self, request):
        """Step 2: Return pre-generated product name"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            product_data = upload_data.get('product_data', {})
            
            generated_name = product_data.get('name', 'Product Name')
            
            # Update step
            upload_data['step'] = 3
            request.session['product_upload_data'] = upload_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'generated_name': generated_name,
                'next_step': 3
            })
            
        except Exception as e:
            print(f"Error in AI name step: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to load product name'})
    
    def _handle_ai_description_generation(self, request):
        """Step 3: Return pre-generated product description"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            
            # Check if user edited the name in step 2
            edited_name = request.POST.get('edited_name')
            if edited_name:
                upload_data['product_data']['name'] = edited_name
                request.session['product_upload_data'] = upload_data
                request.session.modified = True
            
            product_data = upload_data.get('product_data', {})
            generated_description = product_data.get('description', 'Product description')
            
            # Update step
            upload_data['step'] = 4
            request.session['product_upload_data'] = upload_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'generated_description': generated_description,
                'next_step': 4
            })
            
        except Exception as e:
            print(f"Error in AI description step: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to load product description'})
    
    def _handle_ai_category_generation(self, request):
        """Step 4: Return pre-generated product category"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            
            # Check if user edited the description in step 3
            edited_description = request.POST.get('edited_description')
            if edited_description:
                upload_data['product_data']['description'] = edited_description
                request.session['product_upload_data'] = upload_data
                request.session.modified = True
            
            product_data = upload_data.get('product_data', {})
            category_id = product_data.get('suggested_category_id')
            category_name = product_data.get('suggested_category_name', 'General')
            
            # Update step
            upload_data['step'] = 5
            request.session['product_upload_data'] = upload_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'suggested_category_id': category_id,
                'suggested_category_name': category_name,
                'next_step': 5
            })
            
        except Exception as e:
            print(f"Error in AI category step: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to load product category'})
    
    def _handle_ai_price_generation(self, request):
        """Step 5: Return pre-generated product price"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            
            # Check if user edited the category in step 4
            edited_category_id = request.POST.get('edited_category_id')
            edited_category_name = request.POST.get('edited_category_name')
            if edited_category_id and edited_category_name:
                upload_data['product_data']['suggested_category_id'] = edited_category_id
                upload_data['product_data']['suggested_category_name'] = edited_category_name
                request.session['product_upload_data'] = upload_data
                request.session.modified = True
            
            product_data = upload_data.get('product_data', {})
            suggested_price = product_data.get('price', 100.0)
            suggested_offer_price = product_data.get('offer_price', 85.0)
            
            # Update step
            upload_data['step'] = 6
            request.session['product_upload_data'] = upload_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'suggested_price': suggested_price,
                'suggested_offer_price': suggested_offer_price,
                'next_step': 6
            })
            
        except Exception as e:
            print(f"Error in AI price step: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to load product price'})
    
    def _handle_quantity_input(self, request):
        """Step 6: Handle quantity input"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            
            # Check if user edited the prices in step 5
            edited_price = request.POST.get('edited_price')
            edited_offer_price = request.POST.get('edited_offer_price')
            if edited_price:
                upload_data['product_data']['price'] = float(edited_price)
            if edited_offer_price:
                upload_data['product_data']['offer_price'] = float(edited_offer_price)
            
            quantity = request.POST.get('quantity')
            
            if not quantity or int(quantity) < 1:
                return JsonResponse({'success': False, 'error': 'Please enter a valid quantity (minimum 1)'})
            
            # Store quantity
            upload_data['product_data']['stock_quantity'] = int(quantity)
            upload_data['step'] = 7
            request.session['product_upload_data'] = upload_data
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'quantity': int(quantity),
                'next_step': 7
            })
            
        except Exception as e:
            print(f"Error in quantity input: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to save quantity'})
    
    def _handle_final_submission(self, request):
        """Step 7: Final submission and save to database"""
        try:
            upload_data = request.session.get('product_upload_data', {})
            
            # Get form data (user can edit AI-generated content)
            name = request.POST.get('name') or upload_data.get('product_data', {}).get('name', '')
            description = request.POST.get('description') or upload_data.get('product_data', {}).get('description', '')
            price = float(request.POST.get('price') or upload_data.get('product_data', {}).get('price', 0))
            offer_price = request.POST.get('offer_price')
            category_id = request.POST.get('category') or upload_data.get('product_data', {}).get('suggested_category_id')
            stock_quantity = upload_data.get('product_data', {}).get('stock_quantity', 1)
            
            if offer_price:
                offer_price = float(offer_price)
            else:
                offer_price = upload_data.get('product_data', {}).get('offer_price')
            
            # Validate required fields
            if not name or not description or not price:
                return JsonResponse({'success': False, 'error': 'Please fill all required fields'})
            
            # Create product
            # For demo purposes, use a test user or create one
            from django.contrib.auth import get_user_model
            User = get_user_model()
            print("reached till here!!")
            
            # Get current user or create a demo user
            if request.user.is_authenticated:
                user = request.user
            else:
                # Create or get a demo user for testing
                user, created = User.objects.get_or_create(
                    phone_number='demo_user',
                    defaults={
                        'first_name': 'Demo',
                        'last_name': 'User',
                        'is_active': True
                    }
                )
            
            from catalogue.models import CategoryModel
            
            category = None
            if category_id:
                category = CategoryModel.objects.filter(id=category_id).first()
            
            if not category:
                # Fallback if hardcoded category doesn't exist
                category = CategoryModel.objects.filter(is_active=True).first()
                if not category:
                    category, _ = CategoryModel.objects.get_or_create(
                        name="Uncategorized",
                        defaults={'is_active': True}
                    )

            product = ProductModel.objects.create(
                user=user,
                name=name,
                description=description,
                price=price,
                offer_price=offer_price,
                stock_quantity=stock_quantity,
                category=category,
                ai_generated_name=upload_data.get('product_data', {}).get('ai_generated_name', False),
                ai_generated_description=upload_data.get('product_data', {}).get('ai_generated_description', False),
                ai_generated_price=upload_data.get('product_data', {}).get('ai_generated_price', False),
                ai_generated_category=upload_data.get('product_data', {}).get('ai_generated_category', False),
                status='ACTIVE'
            )
            
            # Save images
            from django.core.files.base import ContentFile
            import base64
            import uuid
            
            images = upload_data.get('images', [])
            for i, image_base64 in enumerate(images):
                try:
                    # Extract base64 data
                    format, imgstr = image_base64.split(';base64,')
                    ext = format.split('/')[-1]
                    img_data = ContentFile(base64.b64decode(imgstr), name=f'product_{product.id}_{uuid.uuid4()}.{ext}')

                    ProductMediaModel.objects.create(
                        product=product,
                        image=img_data,
                        is_primary=(i == 0),  # First image is primary
                        display_order=i,
                        alt_text=f"{product.name} - Image {i+1}"
                    )
                except Exception as img_error:
                    print(f"Error saving image {i}: {img_error}")
            
            # Save videos (if any)
            videos = upload_data.get('videos', [])
            for i, video_base64 in enumerate(videos):
                try:
                    format, vidstr = video_base64.split(';base64,')
                    ext = format.split('/')[-1]
                    vid_data = ContentFile(base64.b64decode(vidstr), name=f'product_video_{product.id}_{uuid.uuid4()}.{ext}')

                    ProductMediaModel.objects.create(
                        product=product,
                        video=vid_data,
                        display_order=i,
                        title=f"{product.name} - Video {i+1}"
                    )
                except Exception as vid_error:
                    print(f"Error saving video {i}: {vid_error}")
            
            # Trigger notification
            try:
                from communications.utils import create_seller_notification
                primary_media = ProductMediaModel.objects.filter(product=product, is_primary=True).first()
                image = primary_media.image if primary_media and primary_media.image else None
                create_seller_notification(
                    seller=product.user,
                    title="उत्पाद सफलतापूर्वक जोड़ा गया",
                    message=f"आपका उत्पाद '{product.name}' सफलतापूर्वक जोड़ दिया गया है।",
                    category="PRODUCT_ADDED",
                    image=image
                )
            except Exception as notify_error:
                print(f"Failed to create notification: {notify_error}")

            # Clear session data
            if 'product_upload_data' in request.session:
                del request.session['product_upload_data']
            
            return JsonResponse({
                'success': True,
                'message': 'Product uploaded successfully!',
                'redirect_url': f'/list/',  # Redirect to product list
                'product_id': product.id
            })
            
        except Exception as e:
            print(f"Error in final submission: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to save product'})

    def _generate_all_ai_content(self, images):
        """Generate all AI content at once: name, description, category, and price"""
        try:
            if not images:
                return {'success': False, 'error': 'No images provided for AI processing'}
            
            from dotenv import load_dotenv
            import google.generativeai as genai
            import os
            import json
            import base64
            from io import BytesIO
            from PIL import Image
            
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return {'success': False, 'error': 'Gemini API key not configured'}
            
            genai.configure(api_key=api_key)
            
            # Get available categories for AI selection
            categories = CategoryModel.objects.filter(is_active=True).values_list('name', flat=True)
            categories_list = ', '.join(categories)
            
            # Create comprehensive prompt for all content generation
            # Detect user's preferred language from cookies (default to English)
            user_language = 'english'
            cookie_lang = getattr(self, 'request', None) and self.request.COOKIES.get('garuda_language')
            if cookie_lang:
                user_language = cookie_lang.lower()
            # Map cookie language to language names if needed
            language_map = {
                'hindi': 'Hindi',
                'english': 'English',
                'marathi': 'Marathi',
                'gujarati': 'Gujarati',
                'bengali': 'Bengali',
                'punjabi': 'Punjabi',
                'tamil': 'Tamil',
                'telugu': 'Telugu',
                'kannada': 'Kannada',
                'malayalam': 'Malayalam',
                'urdu': 'Urdu',
                'oriya': 'Odia',
                'assamese': 'Assamese',
                'sanskrit': 'Sanskrit',
            }
            language_name = language_map.get(user_language, 'English')

            prompt = f"""
            Analyze the product images and generate the following information in JSON format for a handcrafted artisan product:

            1. "name": A short, catchy product name (maximum 5 words).
            2. "description": An artisan-friendly description combining:
               - A natural-sounding short description that highlights craftsmanship and traditional techniques.
               - Detailed Description.
               - Materials used.
               - Craft Type.
               - Care Instructions.
               - SEO Keywords / Tags.
               Format this description nicely using markdown, avoiding exaggerated marketing language. Make it suitable for an artisan marketplace.
            3. "category": The most appropriate category from this list: {categories_list}
            4. "price": A reasonable price in Indian Rupees (just the number, no currency symbol).
            5. "offer_price": An offer price that's 10-20% lower than the main price.

            IMPORTANT: Respond ONLY in {language_name}. All fields must be in {language_name}. Do not use any other language.
            Return ONLY a valid JSON object with these exactly 5 keys: name, description, category, price, offer_price. Be accurate and realistic with pricing. Do not include markdown code block syntax (like ```json), just return the raw JSON object.
            """
            
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            content_list = [prompt]
            
            # Add first 3 images to avoid token limits
            for image_base64 in images[:3]:
                try:
                    format, imgstr = image_base64.split(';base64,')
                    img_data = base64.b64decode(imgstr)
                    img = Image.open(BytesIO(img_data))
                    content_list.append(img)
                except Exception as img_error:
                    print(f"Error parsing image for Gemini: {img_error}")
            
            response = model.generate_content(content_list)
            
            ai_response = response.text.strip()
            
            # Clean and parse JSON response
            if ai_response.startswith('```json'):
                ai_response = ai_response.replace('```json', '').replace('```', '').strip()
            elif ai_response.startswith('```'):
                ai_response = ai_response.replace('```', '').strip()
            
            try:
                ai_data = json.loads(ai_response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {'success': False, 'error': 'Failed to parse AI response'}
            
            # Validate and process the AI response
            name = ai_data.get('name', 'Product Name').strip()
            description = ai_data.get('description', 'Product description').strip()
            suggested_category_name = ai_data.get('category', '').strip()
            price = float(ai_data.get('price', 100))
            offer_price = float(ai_data.get('offer_price', price * 0.85))
            
            # Find matching category in database
            category_id = None
            category_name = "General"
            
            if suggested_category_name:
                try:
                    # Try exact match first
                    category = CategoryModel.objects.filter(
                        name__iexact=suggested_category_name, 
                        is_active=True
                    ).first()
                    
                    if not category:
                        # Try partial matching
                        category = CategoryModel.objects.filter(
                            name__icontains=suggested_category_name, 
                            is_active=True
                        ).first()
                    
                    if not category:
                        # Try reverse partial matching
                        for cat in CategoryModel.objects.filter(is_active=True):
                            if cat.name.lower() in suggested_category_name.lower():
                                category = cat
                                break
                    
                    if category:
                        category_id = category.id
                        category_name = category.name
                    else:
                        # Default fallback
                        default_category = CategoryModel.objects.filter(is_active=True).first()
                        if default_category:
                            category_id = default_category.id
                            category_name = default_category.name
                            
                except Exception as cat_error:
                    print(f"Category matching error: {cat_error}")
                    # Use default category
                    default_category = CategoryModel.objects.filter(is_active=True).first()
                    if default_category:
                        category_id = default_category.id
                        category_name = default_category.name
            
            # Trigger AI Success Notification
            if hasattr(self, 'request') and self.request.user.is_authenticated:
                try:
                    from communications.utils import create_seller_notification
                    create_seller_notification(
                        seller=self.request.user,
                        title="AI जनरेशन पूरा हुआ",
                        message=f"आपके उत्पाद के लिए AI विवरण सफलतापूर्वक जनरेट कर दिए गए हैं।",
                        category="AI_GENERATION_COMPLETED"
                    )
                except Exception as notify_error:
                    print(f"Failed to create notification: {notify_error}")
                    
            # Return all generated content
            return {
                'success': True,
                'data': {
                    'name': name,
                    'description': description,
                    'suggested_category_id': category_id,
                    'suggested_category_name': category_name,
                    'price': price,
                    'offer_price': offer_price,
                    'ai_generated_name': True,
                    'ai_generated_description': True,
                    'ai_generated_category': True,
                    'ai_generated_price': True
                }
            }
            
        except Exception as e:
            import traceback
            with open('gemini_error.txt', 'w') as f:
                f.write(traceback.format_exc())
            print(f"Error in AI content generation: {e}")
            if hasattr(self, 'request') and self.request.user.is_authenticated:
                try:
                    from communications.utils import create_seller_notification
                    create_seller_notification(
                        seller=self.request.user,
                        title="AI जनरेशन विफल",
                        message="आपके उत्पाद के लिए AI विवरण जनरेट करने में त्रुटि आई। कृपया पुनः प्रयास करें।",
                        category="AI_GENERATION_FAILED"
                    )
                except Exception as notify_error:
                    print(f"Failed to create notification: {notify_error}")
                    
            return {'success': False, 'error': f'Failed to generate AI content: {str(e)}'}

class ProductListView(SellerRequiredMixin, ListView):
    """List all products with pagination and filtering"""
    model = ProductModel
    template_name = 'product_listing/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ProductModel.objects.filter(user=self.request.user, status='ACTIVE').select_related('category', 'user').prefetch_related('media')
        
        # Search functionality
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__name__icontains=search)
            )
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryModel.objects.filter(is_active=True)
        context['search_query'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        return context

class ProductUploadDebugView(SellerRequiredMixin, View):
    """Debug version of the upload wizard"""
    
    def get(self, request):
        return render(request, 'product_listing/upload_debug.html')

class ProductDetailView(SellerRequiredMixin, DetailView):
    """Detailed view of a single product with all information"""
    model = ProductModel
    template_name = 'product_listing/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return ProductModel.objects.filter(user=self.request.user, status='ACTIVE').select_related('category', 'user').prefetch_related('media')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get all images and videos from ProductMediaModel
        context['product_image_objects'] = product.media.filter(media_type='IMAGE').order_by('display_order')
        context['product_video_objects'] = product.media.filter(media_type='VIDEO').order_by('display_order')
        
        
        # Check if current user owns this product
        context['is_owner'] = (
            self.request.user.is_authenticated and 
            self.request.user == product.user
        )
        
        # Product statistics
        context['total_images'] = context['product_image_objects'].count()
        context['total_videos'] = context['product_video_objects'].count()
        
        # AI generation indicators
        context['ai_indicators'] = {
            'name': product.ai_generated_name,
            'description': product.ai_generated_description,
            'category': product.ai_generated_category,
            'price': product.ai_generated_price,
        }
        
        return context

class ProductEditView(SellerRequiredMixin, UpdateView):
    """Edit product details"""
    model = ProductModel
    template_name = 'product_listing/product_edit.html'
    fields = ['name', 'description', 'price', 'offer_price', 'stock_quantity', 'category']
    context_object_name = 'product'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Add CSS classes to form fields
        form.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter product name',
            'maxlength': '200'
        })
        form.fields['description'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Describe your product...',
            'rows': '4'
        })
        form.fields['price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00',
            'min': '0',
            'step': '0.01'
        })
        form.fields['offer_price'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00 (optional)',
            'min': '0',
            'step': '0.01'
        })
        form.fields['stock_quantity'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0',
            'min': '0'
        })
        form.fields['category'].widget.attrs.update({
            'class': 'form-control'
        })
        
        return form
    
    def get_queryset(self):
        # Only allow editing own products
        if self.request.user.is_authenticated:
            return ProductModel.objects.filter(user=self.request.user, status='ACTIVE')
        return ProductModel.objects.none()
    
    def get_success_url(self):
        messages.success(self.request, 'Product updated successfully!')
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Get categories for dropdown
        context['categories'] = CategoryModel.objects.filter(is_active=True)
        
        # Get all images and videos for preview from ProductMediaModel
        context['product_image_objects'] = product.media.filter(media_type='IMAGE').order_by('display_order')
        context['product_video_objects'] = product.media.filter(media_type='VIDEO').order_by('display_order')
        
        # AI generation indicators
        context['ai_indicators'] = {
            'name': product.ai_generated_name,
            'description': product.ai_generated_description,
            'category': product.ai_generated_category,
            'price': product.ai_generated_price,
        }
        
        return context
    
    def form_valid(self, form):
        # Update AI generation flags if user modifies AI-generated content
        if 'name' in form.changed_data and self.object.ai_generated_name:
            self.object.ai_generated_name = False
        if 'description' in form.changed_data and self.object.ai_generated_description:
            self.object.ai_generated_description = False
        if 'category' in form.changed_data and self.object.ai_generated_category:
            self.object.ai_generated_category = False
        if 'price' in form.changed_data or 'offer_price' in form.changed_data:
            if self.object.ai_generated_price:
                self.object.ai_generated_price = False
        
        response = super().form_valid(form)
        
        try:
            from communications.utils import create_seller_notification
            primary_media = self.object.media.filter(media_type='IMAGE', is_primary=True).first()
            if not primary_media:
                primary_media = self.object.media.filter(media_type='IMAGE').first()
            image = primary_media.image if primary_media and primary_media.image else None
            create_seller_notification(
                seller=self.object.user,
                title="उत्पाद अपडेट किया गया",
                message=f"आपका उत्पाद '{self.object.name}' सफलतापूर्वक अपडेट हो गया है।",
                category="PRODUCT_UPDATED",
                image=image
            )
        except Exception as notify_error:
            print(f"Failed to create notification: {notify_error}")
            
        return response

class ProductDeleteView(SellerRequiredMixin, DeleteView):
    """Delete a product (soft delete by changing status)"""
    model = ProductModel
    template_name = 'product_listing/product_delete.html'
    context_object_name = 'product'
    success_url = reverse_lazy('product_list')
    
    def get_queryset(self):
        # Only allow deleting own products
        if self.request.user.is_authenticated:
            return ProductModel.objects.filter(user=self.request.user, status='ACTIVE')
        return ProductModel.objects.none()
    
    def delete(self, request, *args, **kwargs):
        # Soft delete by changing status instead of actual deletion
        self.object = self.get_object()
        self.object.status = 'DELETED'
        self.object.save()
        
        try:
            from communications.utils import create_seller_notification
            create_seller_notification(
                seller=self.object.user,
                title="उत्पाद हटाया गया",
                message=f"आपका उत्पाद '{self.object.name}' सफलतापूर्वक हटा दिया गया है।",
                category="PRODUCT_DELETED"
            )
        except Exception as notify_error:
            print(f"Failed to create notification: {notify_error}")
            
        messages.success(request, f'Product "{self.object.name}" has been deleted successfully!')
        return redirect(self.success_url)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        # Get images for preview in delete confirmation (use media relation)
        image_qs = product.media.filter(media_type='IMAGE').order_by('display_order')
        context['images'] = image_qs[:3]  # Show first 3 images
        context['total_images'] = image_qs.count()
        return context

@method_decorator(csrf_exempt, name='dispatch')
class ProductMediaManagementView(SellerRequiredMixin, View):
    """Handle adding, removing, and reordering product media"""
    
    def post(self, request, pk):
        """Handle media operations: add, remove, reorder"""
        try:
            # Get product and verify ownership
            product = get_object_or_404(ProductModel, pk=pk, user=request.user, status='ACTIVE')
            
            action = request.POST.get('action')
            
            if action == 'add_image':
                return self._add_image(request, product)
            elif action == 'remove_image':
                return self._remove_image(request, product)
            elif action == 'add_video':
                return self._add_video(request, product)
            elif action == 'remove_video':
                return self._remove_video(request, product)
            elif action == 'reorder_images':
                return self._reorder_images(request, product)
            elif action == 'reorder_videos':
                return self._reorder_videos(request, product)
            elif action == 'set_primary_image':
                return self._set_primary_image(request, product)
            else:
                return JsonResponse({'success': False, 'error': 'Invalid action'})
                
        except ProductModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Product not found or access denied'})
        except Exception as e:
            print(f"Error in media management: {e}")
            return JsonResponse({'success': False, 'error': 'Server error occurred'})
    
    def _add_image(self, request, product):
        """Add a new image to the product"""
        try:
            image_data = request.POST.get('image')
            alt_text = request.POST.get('alt_text', '')
            
            if not image_data:
                return JsonResponse({'success': False, 'error': 'No image data provided'})
            
            # Parse base64 image
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            img_file = ContentFile(base64.b64decode(imgstr), name=f'product_{product.id}_{uuid.uuid4()}.{ext}')
            
            # Get next display order
            last_image = product.media.filter(media_type='IMAGE').order_by('-display_order').first()
            next_order = (last_image.display_order + 1) if last_image else 0
            
            # Create image
            image = ProductMediaModel.objects.create(
                product=product,
                media_type='IMAGE',
                image=img_file,
                alt_text=alt_text or f"{product.name} - Image {next_order + 1}",
                display_order=next_order,
                is_primary=(not product.media.filter(media_type='IMAGE').exists())  # Make primary if it's the first image
            )
            
            return JsonResponse({
                'success': True,
                'image': {
                    'id': image.id,
                    'url': image.image.url,
                    'alt_text': image.alt_text,
                    'is_primary': image.is_primary,
                    'display_order': image.display_order
                }
            })
            
        except Exception as e:
            print(f"Error adding image: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to add image'})
    
    def _remove_image(self, request, product):
        """Remove an image from the product"""
        try:
            image_id = request.POST.get('image_id')
            
            if not image_id:
                return JsonResponse({'success': False, 'error': 'No image ID provided'})
            
            image = ProductMediaModel.objects.get(id=image_id, product=product, media_type='IMAGE')
            was_primary = image.is_primary
            image.delete()
            
            # If we deleted the primary image, make another image primary
            if was_primary:
                first_image = product.media.filter(media_type='IMAGE').first()
                if first_image:
                    first_image.is_primary = True
                    first_image.save()
            
            return JsonResponse({'success': True, 'message': 'Image removed successfully'})

        except ProductMediaModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
        except Exception as e:
            print(f"Error removing image: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to remove image'})
    
    def _add_video(self, request, product):
        """Add a new video to the product"""
        try:
            video_data = request.POST.get('video')
            title = request.POST.get('title', '')
            
            if not video_data:
                return JsonResponse({'success': False, 'error': 'No video data provided'})
            
            # Parse base64 video
            format, vidstr = video_data.split(';base64,')
            ext = format.split('/')[-1]
            vid_file = ContentFile(base64.b64decode(vidstr), name=f'product_video_{product.id}_{uuid.uuid4()}.{ext}')
            
            # Get next display order
            last_video = product.videos.order_by('-display_order').first()
            next_order = (last_video.display_order + 1) if last_video else 0
            
            # Create video
            video = ProductMediaModel.objects.create(
                product=product,
                video=vid_file,
                title=title or f"{product.name} - Video {next_order + 1}",
                display_order=next_order
            )
            
            return JsonResponse({
                'success': True,
                'video': {
                    'id': video.id,
                    'url': video.video.url,
                    'title': video.title,
                    'display_order': video.display_order
                }
            })
            
        except Exception as e:
            print(f"Error adding video: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to add video'})
    
    def _remove_video(self, request, product):
        """Remove a video from the product"""
        try:
            video_id = request.POST.get('video_id')
            
            if not video_id:
                return JsonResponse({'success': False, 'error': 'No video ID provided'})
            
            video = ProductMediaModel.objects.get(id=video_id, product=product, media_type='video')
            video.delete()
            
            return JsonResponse({'success': True, 'message': 'Video removed successfully'})
            
        except ProductMediaModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Video not found'})
        except Exception as e:
            print(f"Error removing video: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to remove video'})
    
    def _reorder_images(self, request, product):
        """Reorder product images"""
        try:
            image_ids = json.loads(request.POST.get('image_ids', '[]'))
            
            for index, image_id in enumerate(image_ids):
                ProductMediaModel.objects.filter(id=image_id, product=product, media_type='image').update(display_order=index)

            return JsonResponse({'success': True, 'message': 'Images reordered successfully'})
            
        except Exception as e:
            print(f"Error reordering images: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to reorder images'})
    
    def _reorder_videos(self, request, product):
        """Reorder product videos"""
        try:
            video_ids = json.loads(request.POST.get('video_ids', '[]'))
            
            for index, video_id in enumerate(video_ids):
                ProductMediaModel.objects.filter(id=video_id, product=product, media_type='video').update(display_order=index)

            return JsonResponse({'success': True, 'message': 'Videos reordered successfully'})
            
        except Exception as e:
            print(f"Error reordering videos: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to reorder videos'})
    
    def _set_primary_image(self, request, product):
        """Set an image as primary"""
        try:
            image_id = request.POST.get('image_id')
            
            if not image_id:
                return JsonResponse({'success': False, 'error': 'No image ID provided'})
            
            # Remove primary flag from all images
            product.images.update(is_primary=False)
            
            # Set new primary image
            image = ProductMediaModel.objects.get(id=image_id, product=product, media_type='image')
            image.is_primary = True
            image.save()
            
            return JsonResponse({'success': True, 'message': 'Primary image updated successfully'})

        except ProductMediaModel.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Image not found'})
        except Exception as e:
            print(f"Error setting primary image: {e}")
            return JsonResponse({'success': False, 'error': 'Failed to set primary image'})


class VerificationProgressView(SellerRequiredMixin, View):
    template_name = 'seller/verification_progress.html'

    def get(self, request, *args, **kwargs):
        return redirect('upload_wizard')

    def post(self, request, *args, **kwargs):
        return redirect('upload_wizard')
        






@method_decorator(csrf_exempt, name='dispatch')
class ManualProductUploadWizardView(SellerRequiredMixin, View):
    """Multi-step manual product upload wizard"""
    
    def get(self, request):
        """Load the manual stepper UI"""
        if not request.user.is_authenticated:
            return redirect('login')
            
        context = {
            'categories': CategoryModel.objects.filter(is_active=True),
        }
        return render(request, 'product_listing/manual_upload_wizard.html', context)
    
    def post(self, request):
        """Handle AJAX final submission"""
        try:
            name = request.POST.get('name')
            description = request.POST.get('description')
            price_str = request.POST.get('price')
            offer_str = request.POST.get('offer')
            quantity_str = request.POST.get('quantity')
            category_id = request.POST.get('category')
            
            if not name or not description or not price_str or not quantity_str:
                return JsonResponse({'success': False, 'error': 'Please fill all required fields'})
                
            price = float(price_str)
            stock_quantity = int(quantity_str)
            
            offer_price = None
            if offer_str:
                if '%' in offer_str:
                    percentage = float(offer_str.replace('%', '').strip())
                    offer_price = price * (1 - (percentage / 100.0))
                else:
                    offer_price = float(offer_str)
                    
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if request.user.is_authenticated:
                user = request.user
            else:
                user, created = User.objects.get_or_create(
                    phone_number='demo_user',
                    defaults={'first_name': 'Demo', 'last_name': 'User', 'is_active': True}
                )
                
            from catalogue.models import CategoryModel
            category = None
            if category_id:
                category = CategoryModel.objects.filter(id=category_id).first()
            if not category:
                category = CategoryModel.objects.filter(is_active=True).first()
                if not category:
                    category, _ = CategoryModel.objects.get_or_create(
                        name="Uncategorized",
                        defaults={'is_active': True}
                    )
            
            product = ProductModel.objects.create(
                user=user,
                name=name,
                description=description,
                price=price,
                offer_price=offer_price,
                stock_quantity=stock_quantity,
                category=category,
                status='ACTIVE'
            )
            
            # Save media
            from django.core.files.base import ContentFile
            import base64
            import uuid
            
            images = request.POST.getlist('images[]')
            if not images:
                images = request.POST.getlist('images')
                
            for i, image_base64 in enumerate(images):
                try:
                    if ';base64,' in image_base64:
                        format, imgstr = image_base64.split(';base64,')
                        ext = format.split('/')[-1]
                        img_data = ContentFile(base64.b64decode(imgstr), name=f'product_{product.id}_{uuid.uuid4()}.{ext}')
                        ProductMediaModel.objects.create(
                            product=product,
                            image=img_data,
                            media_type='IMAGE',
                            is_primary=(i == 0),
                            display_order=i,
                            alt_text=f"{product.name} - Image {i+1}"
                        )
                except Exception as img_error:
                    print(f"Error saving image {i}: {img_error}")
                    
            videos = request.POST.getlist('videos[]')
            if not videos:
                videos = request.POST.getlist('videos')
                
            for i, video_base64 in enumerate(videos):
                try:
                    if ';base64,' in video_base64:
                        format, vidstr = video_base64.split(';base64,')
                        ext = format.split('/')[-1]
                        vid_data = ContentFile(base64.b64decode(vidstr), name=f'product_video_{product.id}_{uuid.uuid4()}.{ext}')
                        ProductMediaModel.objects.create(
                            product=product,
                            video=vid_data,
                            media_type='VIDEO',
                            display_order=i,
                            title=f"{product.name} - Video {i+1}"
                        )
                except Exception as vid_error:
                    print(f"Error saving video {i}: {vid_error}")
                    
            # Notification
            try:
                from communications.utils import create_seller_notification
                primary_media = ProductMediaModel.objects.filter(product=product, media_type='IMAGE', is_primary=True).first()
                image = primary_media.image if primary_media and primary_media.image else None
                create_seller_notification(
                    seller=product.user,
                    title="उत्पाद सफलतापूर्वक जोड़ा गया",
                    message=f"आपका उत्पाद '{product.name}' सफलतापूर्वक जोड़ दिया गया है।",
                    category="PRODUCT_ADDED",
                    image=image
                )
            except Exception as notify_error:
                print(f"Failed to create notification: {notify_error}")
                
            return JsonResponse({
                'success': True,
                'message': 'Product uploaded successfully!',
                'redirect_url': '/list/',
                'product_id': product.id
            })
            
        except Exception as e:
            print(f"Error in ManualProductUploadWizardView: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

# ======================================================= Seller Help Views =======================================================

class SellerHelpView(SellerRequiredMixin, TemplateView):
    template_name = 'seller/help.html'

class SellerHelpAPIView(SellerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json
        import google.generativeai as genai
        from dotenv import load_dotenv
        import os
        from django.http import JsonResponse
        
        try:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({'success': False, 'error': 'API Key not found'})

            data = json.loads(request.body)
            message = data.get('message', '')
            history = data.get('history', [])
            cookie_lang = request.COOKIES.get('garuda_language')
            user_language = cookie_lang.lower() if cookie_lang else 'hindi'
            
            language_map = {
                'hindi': 'Hindi using Devanagari script',
                'marathi': 'Marathi using Devanagari script',
                'gujarati': 'Gujarati using Gujarati script',
                'bengali': 'Bengali using Bengali script',
                'punjabi': 'Punjabi using Gurmukhi script',
                'tamil': 'Tamil using Tamil script',
                'telugu': 'Telugu using Telugu script',
                'kannada': 'Kannada using Kannada script',
                'malayalam': 'Malayalam using Malayalam script',
                'urdu': 'Urdu using Urdu script',
                'oriya': 'Odia using Odia script',
                'assamese': 'Assamese using Assamese script',
                'sanskrit': 'Sanskrit using Devanagari script',
                'english': 'English'
            }
            language = language_map.get(user_language, 'Hindi using Devanagari script')
            
            genai.configure(api_key=api_key)
            
            system_instruction = f"""
            You are Garud Sahayak, the AI assistant for the Garud Seller Application.
            Your job is to help sellers use the Garud platform.
            Answer questions related to:
            • Product Upload
            • Manual Product Upload
            • AI Product Upload
            • Product List
            • Notifications
            • Orders
            • Profile
            • Language
            • Payments
            • Account Settings
            • Seller Features

            Respond in a short, friendly and helpful manner.
            If the seller asks something unrelated to Garud, politely inform them that you can only answer Garud-related questions.

            The seller's selected application language is {language}.
            IMPORTANT:
            Respond ONLY in {language}.
            Do NOT use English unless the seller explicitly requests it.
            All responses must be in natural {language}.
            """
            
            model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=system_instruction)
            
            gemini_history = []
            for msg in history:
                role = 'user' if msg.get('isUser') else 'model'
                gemini_history.append({'role': role, 'parts': [msg.get('text')]})
            
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(message)
            
            return JsonResponse({'success': True, 'response': response.text.strip()})
        except Exception as e:
            print(f"Error in SellerHelpAPIView: {e}")
            return JsonResponse({'success': False, 'error': "क्षमा करें, कुछ गलत हो गया। कृपया पुनः प्रयास करें।"})

class CustomerSearchHistoryDeleteView(CustomerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        query = request.POST.get('query')
        if query:
            from account.models import SearchHistoryModel
            SearchHistoryModel.objects.filter(user=request.user, query=query).delete()
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'error': 'Query not provided'})

class CustomerSearchHistoryClearView(CustomerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from account.models import SearchHistoryModel
        SearchHistoryModel.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True})

class CustomerCameraSearchView(CustomerRequiredMixin, TemplateView):
    template_name = 'costuner_flow/camera_search.html'

class CustomerCameraSearchAPIView(CustomerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        import json
        import base64
        import cv2
        import numpy as np
        
        try:
            data = json.loads(request.body)
            image_data = data.get('image')
            
            if not image_data:
                return JsonResponse({'success': False, 'error': 'No image provided'})
                
            if ',' in image_data:
                image_data = image_data.split(',')[1]
                
            img_bytes = base64.b64decode(image_data)
            
            # --- 1. QR Code Detection ---
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            detector = cv2.QRCodeDetector()
            qr_data, bbox, _ = detector.detectAndDecode(img)
            
            if qr_data:
                return JsonResponse({'success': True, 'type': 'qr', 'data': qr_data.strip()})
                
            # --- 2. Visual Search via Gemini ---
            from dotenv import load_dotenv
            import google.generativeai as genai
            from PIL import Image
            import io
            import os
            
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                return JsonResponse({'success': False, 'error': 'Gemini API not configured'})
                
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            pil_img = Image.open(io.BytesIO(img_bytes))
            
            prompt = """
            You are a visual search assistant for an e-commerce platform specializing in handicrafts, pottery, decor, and fashion.
            Analyze this image and identify the main product. 
            Describe its Overall shape, Colour, Pattern, Texture, Craft Type, Material, and Product Category.
            Return ONLY a concise comma-separated list of these descriptive features (e.g., 'vase, blue, ceramic, floral pattern, smooth, handmade').
            If no clear product is visible, output '__NO_MATCH__'.
            """
            
            response = model.generate_content([prompt, pil_img])
            description = response.text.strip()
            
            if description == '__NO_MATCH__' or not description:
                return JsonResponse({'success': True, 'type': 'visual', 'no_match': True})
                
            # Generate embedding for the description
            embed_model = "models/gemini-embedding-2"
            embed_response = genai.embed_content(
                model=embed_model,
                content=description,
                task_type="retrieval_query",
            )
            query_vector = np.array(embed_response['embedding'])
            
            # Fetch product embeddings from DB
            from catalogue.models import ProductVisualEmbedding
            embeddings = ProductVisualEmbedding.objects.all()
            
            if not embeddings.exists():
                return JsonResponse({'success': True, 'type': 'visual', 'no_match': True})
                
            results = []
            for emb in embeddings:
                if not emb.embedding: continue
                db_vector = np.array(emb.embedding)
                # Cosine similarity
                cosine_sim = np.dot(query_vector, db_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(db_vector))
                results.append((cosine_sim, emb.product.id))
                
            results.sort(key=lambda x: x[0], reverse=True)
            
            # Logic based on confidence
            top_score, top_id = results[0]
            if top_score > 0.85:
                # Exact match
                from django.urls import reverse
                from catalogue.models import SearchHistoryModel
                from django.utils import timezone
                SearchHistoryModel.objects.update_or_create(
                    user=request.user,
                    query="Visual Search",
                    defaults={'updated_at': timezone.now()}
                )
                url = reverse('customer_product_detail', kwargs={'pk': top_id})
                return JsonResponse({'success': True, 'type': 'visual', 'exact_match': True, 'url': url})
            elif top_score > 0.60:
                # Similar matches (top 5)
                similar_ids = [str(r[1]) for r in results[:5] if r[0] > 0.60]
                return JsonResponse({'success': True, 'type': 'visual', 'exact_match': False, 'ids': similar_ids})
            else:
                return JsonResponse({'success': True, 'type': 'visual', 'no_match': True})
            
        except Exception as e:
            print(f"Error in Camera Search API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})


class CustomerWishlistView(CustomerProductSearchView):
    template_name = 'costuner_flow/wishlist.html'

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        from catalogue.models import Wishlist
        wishlist_qs = Wishlist.objects.filter(user=user).first()
        if wishlist_qs:
            wishlist_product_ids = list(wishlist_qs.items.values_list('product_id', flat=True))
            return qs.filter(id__in=wishlist_product_ids)
        return qs.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_wishlist_page'] = True
        return context

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class AddToWishlistView(CustomerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            # Handle both JSON and URL encoded data
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                product_id = data.get('product_id')
            else:
                product_id = request.POST.get('product_id')

            if not product_id:
                return JsonResponse({'success': False, 'message': 'Product ID is required'})

            from catalogue.models import ProductModel, Wishlist, WishlistItem
            product = ProductModel.objects.get(id=product_id)
            wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
            WishlistItem.objects.get_or_create(wishlist=wishlist, product=product)
            return JsonResponse({'success': True, 'message': 'Added to wishlist'})
        except ProductModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

@method_decorator(csrf_exempt, name='dispatch')
class RemoveFromWishlistView(CustomerRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                product_id = data.get('product_id')
            else:
                product_id = request.POST.get('product_id')

            if not product_id:
                return JsonResponse({'success': False, 'message': 'Product ID is required'})

            from catalogue.models import ProductModel, Wishlist, WishlistItem
            product = ProductModel.objects.get(id=product_id)
            wishlist = Wishlist.objects.filter(user=request.user).first()
            if wishlist:
                WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
            return JsonResponse({'success': True, 'message': 'Removed from wishlist'})
        except ProductModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

class CustomerOrderListView(CustomerRequiredMixin, ListView):
    template_name = 'costuner_flow/customer_orders.html'
    context_object_name = 'order_items'
    
    def get_queryset(self):
        from orders.models import OrderItemModel
        qs = OrderItemModel.objects.filter(order__user=self.request.user).select_related('product', 'seller_order', 'order').order_by('-order__created_at')
        
        status_filter = self.request.GET.get('status')
        if status_filter:
            qs = qs.filter(seller_order__status__iexact=status_filter)
            
        date_filter = self.request.GET.get('date_filter')
        if date_filter:
            import datetime
            from django.utils import timezone
            now = timezone.now()
            if date_filter == 'last_30_days':
                qs = qs.filter(order__created_at__gte=now - datetime.timedelta(days=30))
            elif date_filter == 'last_3_months':
                qs = qs.filter(order__created_at__gte=now - datetime.timedelta(days=90))
            else:
                try:
                    year = int(date_filter)
                    qs = qs.filter(order__created_at__year=year)
                except ValueError:
                    pass
                
        return qs

    def render_to_response(self, context, **response_kwargs):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.template.loader import render_to_string
            from django.http import JsonResponse
            html = render_to_string('costuner_flow/partials/order_list_content.html', context, request=self.request)
            return JsonResponse({'html': html})
        return super().render_to_response(context, **response_kwargs)

class CustomerOrderDetailView(CustomerRequiredMixin, View):
    def get(self, request, pk):
        from orders.models import OrderItemModel
        from django.shortcuts import get_object_or_404
        
        # Fetch the requested OrderItem
        order_item = get_object_or_404(OrderItemModel, pk=pk, order__user=request.user)
        
        # The tracking and overall status is based on SellerOrder
        seller_order = order_item.seller_order
        
        # Get all items in this same SellerOrder
        if seller_order:
            order_items = seller_order.items.all().select_related('product')
        else:
            order_items = [order_item]
            
        from account.models import CustomerAddressModel
        
        address = order_item.order.address if order_item.order and hasattr(order_item.order, 'address') and order_item.order.address else None
        
        # Fallback for older orders where address was not saved properly due to AddressModel vs CustomerAddressModel bug
        if not address:
            address = CustomerAddressModel.objects.filter(user=request.user, is_default=True).first()
            if not address:
                address = CustomerAddressModel.objects.filter(user=request.user).first()
            
        context = {
            'order_item': order_item,
            'seller_order': seller_order,
            'order_items': order_items,
            'address': address,
            'order': order_item.order,
        }
        
        return render(request, 'costuner_flow/customer_order_detail.html', context)

class CustomerOrderInfoView(CustomerRequiredMixin, View):
    def get(self, request, pk):
        from orders.models import OrderItemModel
        from django.shortcuts import get_object_or_404
        from account.models import CustomerAddressModel
        
        # Fetch the requested OrderItem
        order_item = get_object_or_404(OrderItemModel, pk=pk, order__user=request.user)
        seller_order = order_item.seller_order
        
        if seller_order:
            order_items = seller_order.items.all().select_related('product')
        else:
            order_items = [order_item]
            
        address = order_item.order.address if order_item.order and hasattr(order_item.order, 'address') and order_item.order.address else None
        if not address:
            address = CustomerAddressModel.objects.filter(user=request.user, is_default=True).first()
            if not address:
                address = CustomerAddressModel.objects.filter(user=request.user).first()
        
        # Calculate subtotal, tax, and discount
        subtotal = sum(item.price * item.quantity for item in order_items)
        
        for item in order_items:
            if item.product and item.product.price and item.product.price > item.price:
                discount_val = ((item.product.price - item.price) / item.product.price) * 100
                item.discount_percentage = int(discount_val)
            else:
                item.discount_percentage = 0
                
        tax = 0.00 # Placeholder for tax if any
        shipping = 0.00
        total = float(subtotal) + tax + shipping
            
        context = {
            'order_item': order_item,
            'seller_order': seller_order,
            'order_items': order_items,
            'address': address,
            'order': order_item.order,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total
        }
        
        return render(request, 'costuner_flow/customer_order_info.html', context)

class DownloadInvoiceView(CustomerRequiredMixin, View):
    def get(self, request, pk):
        from orders.models import OrderItemModel
        from django.shortcuts import get_object_or_404
        from account.models import CustomerAddressModel, GSTModel
        from django.template.loader import render_to_string
        from django.http import HttpResponse
        import io
        
        try:
            from xhtml2pdf import pisa
            # Library successfully imported
        except ImportError:
            return HttpResponse("PDF generation library not installed.", status=500)
            
        # Fetch the requested OrderItem
        order_item = get_object_or_404(OrderItemModel, pk=pk, order__user=request.user)
        seller_order = order_item.seller_order
        
        if seller_order:
            order_items = seller_order.items.all().select_related('product')
            seller = seller_order.seller
        else:
            order_items = [order_item]
            seller = order_item.product.user if order_item.product else None
            
        address = order_item.order.address if order_item.order and hasattr(order_item.order, 'address') and order_item.order.address else None
        if not address:
            address = CustomerAddressModel.objects.filter(user=request.user, is_default=True).first()
            if not address:
                address = CustomerAddressModel.objects.filter(user=request.user).first()
                
        # Seller details
        seller_gst = None
        if seller:
            seller_gst = GSTModel.objects.filter(user=seller).first()
        
        # Calculate subtotal, tax, and discount
        subtotal = sum(item.price * item.quantity for item in order_items)
        discount_total = 0
        
        for item in order_items:
            if item.product and item.product.price and item.product.price > item.price:
                discount_val = ((item.product.price - item.price) / item.product.price) * 100
                item.discount_percentage = int(discount_val)
                item.discount_amount = (item.product.price - item.price) * item.quantity
                discount_total += item.discount_amount
            else:
                item.discount_percentage = 0
                item.discount_amount = 0
                
        tax = 0.00 # Placeholder for tax if any
        shipping = 0.00
        total = float(subtotal) + tax + shipping
            
        context = {
            'order_item': order_item,
            'seller_order': seller_order,
            'order_items': order_items,
            'address': address,
            'order': order_item.order,
            'seller': seller,
            'seller_gst': seller_gst,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total,
            'discount_total': discount_total,
            'customer_name': request.user.profile.full_name if hasattr(request.user, 'profile') and request.user.profile.full_name else (request.user.full_name if hasattr(request.user, 'full_name') and request.user.full_name else request.user.mobile)
        }
        
        html = render_to_string('costuner_flow/invoice_template.html', context)
        
        response = HttpResponse(content_type='application/pdf')
        filename = f"GARUD_Invoice_{order_item.order.pg_order_id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create PDF
        pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response)
        
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
            
        return response

from django.utils import timezone
from datetime import timedelta
import json
from django.http import JsonResponse

class CustomerNotificationView(CustomerRequiredMixin, View):
    def get(self, request):
        from communications.models import CustomerNotification, CustomerNotificationPreference
        
        pref, created = CustomerNotificationPreference.objects.get_or_create(user=request.user)
        notifications = CustomerNotification.objects.filter(user=request.user)
        
        new_notifications = notifications.filter(is_read=False)
        earlier_notifications = notifications.filter(is_read=True)
        
        # Helper to format timestamps relative to now
        now = timezone.now()
        def format_timestamp(created_at):
            if created_at.date() == now.date():
                return created_at.strftime('%I:%M %p')
            elif created_at.date() == (now - timedelta(days=1)).date():
                return "Yesterday"
            else:
                return created_at.strftime('%d %b')
                
        # Format dates for template
        for n in new_notifications:
            n.formatted_time = format_timestamp(n.created_at)
        for n in earlier_notifications:
            n.formatted_time = format_timestamp(n.created_at)
            
        context = {
            'is_notifications_enabled': pref.is_enabled,
            'new_notifications': new_notifications,
            'earlier_notifications': earlier_notifications,
            'new_count': new_notifications.count(),
            'earlier_count': earlier_notifications.count()
        }
        return render(request, 'costuner_flow/customer_notifications.html', context)

class ToggleCustomerNotificationPreference(CustomerRequiredMixin, View):
    def post(self, request):
        from communications.models import CustomerNotificationPreference
        try:
            data = json.loads(request.body)
            pref, created = CustomerNotificationPreference.objects.get_or_create(user=request.user)
            pref.is_enabled = data.get('is_enabled', pref.is_enabled)
            pref.save()
            return JsonResponse({'status': 'success', 'is_enabled': pref.is_enabled})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class MarkCustomerNotificationRead(CustomerRequiredMixin, View):
    def post(self, request, pk):
        from communications.models import CustomerNotification
        try:
            notification = CustomerNotification.objects.get(pk=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'status': 'success', 'target_url': notification.target_url})
        except CustomerNotification.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Not found'}, status=404)
