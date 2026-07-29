from django.urls import path
from django.views.generic import TemplateView
from core.base import functions
from .views import *
from catalogue.function import *
from core.base.functions import *
from account import views
from account.flow_controller import CentralFlowControllerView
from django.conf import settings
from django.conf.urls.static import static
from orders.views import (
    SellerOrderListView,
    SellerOrderDetailView,
    SellerOrderTrackingView,
    SellerOrderStatusUpdateView
)
from account.customer_views import (
    CustomerLoginView, CustomerOTPVerificationView, CustomerSuccessView,
    CustomerMenuView, CustomerLoginSecurityView, CustomerLegalAboutView, CustomerPrivacyNoticeView,
    CustomerAddressListView, CustomerAddressCreateView,
    CustomerAddressUpdateView, CustomerAddressDeleteView, CustomerAddressSetDefaultView,
    CustomerDeleteAccountView, CustomerSwitchAccountView, CustomerSwitchAccountActionView,
    CustomerSwitchAccountRemoveView
)

urlpatterns = [
    path('', SplashView.as_view(), name='splash'),
    path('controller/', CentralFlowControllerView.as_view(), name='central_controller'),
    path('role-selection/', RoleSelectionView.as_view(), name='role_selection'),
    path('seller-welcome/', SellerWelcomeView.as_view(), name='seller_welcome'),
    path('seller-onboarding/<int:step>/', SellerOnboardingStepperView.as_view(), name='seller_onboarding_step'),
    path('language-preference/', LanguagePreferenceView.as_view(), name='language_preference_ajax'),
    path('landing-page/', IndexComponentView.as_view(), name='components_index'),
    path('set-cookie/', setCookie, name='set-cookie'),
    # path('verify-otp/', OtpVerificationView.as_view(), name='otp_verification'),
    path('success/', OnboardingSuccessView.as_view(), name='onboarding_success'),
    path('customer-home/', views.CustomerHomeView.as_view(), name='customer_home'),
    
    # Customer Authentication Flow
    path('customer/login/', CustomerLoginView.as_view(), name='customer_login'),
    path('customer/otp-verification/', CustomerOTPVerificationView.as_view(), name='customer_otp'),
    path('customer/login-success/', CustomerSuccessView.as_view(), name='customer_success'),
    
    # Customer Menu and Profile Flow
    path('customer/search/', CustomerProductSearchView.as_view(), name='customer_search'),
    path('customer/search/history/delete/', CustomerSearchHistoryDeleteView.as_view(), name='delete_search_history'),
    path('customer/search/history/clear/', CustomerSearchHistoryClearView.as_view(), name='clear_search_history'),
    path('customer/search/camera/', CustomerCameraSearchView.as_view(), name='camera_search'),
    path('api/customer/camera-search/', CustomerCameraSearchAPIView.as_view(), name='api_camera_search'),
    path('customer/menu/', CustomerMenuView.as_view(), name='customer_menu'),
    path('customer/login-security/', CustomerLoginSecurityView.as_view(), name='customer_login_security'),
    path('customer/legal-about/', CustomerLegalAboutView.as_view(), name='customer_legal_about'),
    path('customer/privacy-notice/', CustomerPrivacyNoticeView.as_view(), name='customer_privacy_notice'),
    path('customer/address/', CustomerAddressListView.as_view(), name='customer_address_list'),
    path('customer/address/add/', CustomerAddressCreateView.as_view(), name='customer_address_add'),
    path('customer/address/<int:pk>/edit/', CustomerAddressUpdateView.as_view(), name='customer_address_edit'),
    path('customer/address/<int:pk>/remove/', CustomerAddressDeleteView.as_view(), name='customer_address_remove'),
    path('customer/address/<int:pk>/default/', CustomerAddressSetDefaultView.as_view(), name='customer_address_default'),
    path('customer/delete-account/', CustomerDeleteAccountView.as_view(), name='customer_delete_account'),
    
    path('customer-product/<int:pk>/', views.CustomerProductDetailView.as_view(), name='customer_product_detail'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/update/<int:pk>/', CartUpdateQuantityView.as_view(), name='cart_update_quantity'),
    path('cart/remove/<int:pk>/', CartRemoveItemView.as_view(), name='cart_remove_item'),
    
    # Customer Orders Flow
    path('customer/orders/', CustomerOrderListView.as_view(), name='customer_orders'),
    path('customer/orders/<int:pk>/', CustomerOrderDetailView.as_view(), name='customer_order_detail'),
    path('customer/orders/<int:pk>/info/', CustomerOrderInfoView.as_view(), name='customer_order_info'),
    path('customer/orders/<int:pk>/invoice/', DownloadInvoiceView.as_view(), name='customer_download_invoice'),
    
    # Customer Account Switch Flow
    path('customer/switch-account/', CustomerSwitchAccountView.as_view(), name='customer_switch_account'),
    path('customer/switch-account/action/', CustomerSwitchAccountActionView.as_view(), name='customer_switch_account_action'),
    path('customer/switch-account/remove/', CustomerSwitchAccountRemoveView.as_view(), name='customer_switch_account_remove'),
    
    # Customer Wishlist URLs
    path('customer/wishlist/', CustomerWishlistView.as_view(), name='customer_wishlist'),
    path('customer/wishlist/add/', AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('customer/wishlist/remove/', RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
    path('checkout/address/', CheckoutAddressSelectionView.as_view(), name='checkout_address_selection'),
    path('checkout/review/', OrderReviewPlaceholderView.as_view(), name='checkout_review'),
    path('checkout/success/', CheckoutSuccessView.as_view(), name='checkout_success'),
    path('payment/verify/', functions.payment_confirmation, name='payment_verify'),
    path('cart/add/', views.CartAddItemView.as_view(), name='cart_add_item'),


    path('payment/create/', functions.create_order, name='create_order'),

    path('user-profile/', UserProfileDashboardView.as_view(), name='user_profile'),
    path('user-profile-details/', ProfileUpdateView.as_view(), name='user_profile_details'),
    path('lang-settings/', LanguagePreferenceUpdateDashboardView.as_view(), name='language_settings'),
    path('address-settings/', AddressDashboardView.as_view(), name='address_settings'),
    path('privacy-policy/', PrivacyPolicyDashboardView.as_view(), name='privacy_policy'),
    # path('garud_ambassador/', SplashView.as_view(), name='splash'), # done
    
    path('terms-and-conditions/', TermsAndConditionsView.as_view(), name='terms_and_conditions'),
    path('seller-help/', SellerHelpView.as_view(), name='seller_help'),
    path('seller-help/api/', SellerHelpAPIView.as_view(), name='seller_help_api'),
    path('bank-settings/', AccountSettingsView.as_view(), name='account_settings'),
    path('bank-settings/edit/<int:pk>/', BankAccountUpdateView.as_view(), name='edit_bank_account'),
    
    # Unified onboarding stepper
    # path('onboarding/', OnboardingStepperView.as_view(), name='onboarding_stepper'),
    path('verification-progress/', VerificationProgressView.as_view(), name='verification_progress'),

    # Product listing URLs
    path('upload/selection/', TemplateView.as_view(template_name='product_listing/product_selection.html'), name='product_selection'),
    path('upload/manual/', ManualProductUploadWizardView.as_view(), name='manual_upload_wizard'),
    path('upload/', ProductUploadWizardView.as_view(), name='upload_wizard'),
    path('upload/debug/', ProductUploadDebugView.as_view(), name='upload_debug'),
    path('list/', ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('<int:pk>/edit/', ProductEditView.as_view(), name='product_edit'),
    path('<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('<int:pk>/media/', ProductMediaManagementView.as_view(), name='media_management'),
    
    # Seller Order URLs
    path('seller-orders/', SellerOrderListView.as_view(), name='seller_orders_list'),
    path('seller-orders/<int:pk>/', SellerOrderDetailView.as_view(), name='seller_order_detail'),
    path('seller-orders/<int:pk>/track/', SellerOrderTrackingView.as_view(), name='seller_order_tracking'),
    path('seller-orders/<int:pk>/update-status/', SellerOrderStatusUpdateView.as_view(), name='seller_order_status_update'),
    # Customer Notifications URLs
    path('customer/notifications/', CustomerNotificationView.as_view(), name='customer_notifications'),
    path('customer/notifications/toggle/', ToggleCustomerNotificationPreference.as_view(), name='toggle_customer_notifications'),
    path('customer/notifications/read/<int:pk>/', MarkCustomerNotificationRead.as_view(), name='mark_customer_notification_read'),
]






if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)