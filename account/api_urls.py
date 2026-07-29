from django.urls import path, include
from rest_framework.routers import DefaultRouter

from account.api_views import *
from .views import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('get-otp/', GetOTPView.as_view(), name='get-otp'),
    path('check-registration/', CheckRegistrationView.as_view(), name='check-registration'),
    path('login-or-register/', LoginOrRegisterView.as_view(), name='login-or-register'),
    path('set-reset-password/', SetResetPasswordView.as_view(), name='set-reset-password'),
    path('delete-account/', DeleteAccountAPIView.as_view(), name='delete-account'),
    path('logout/', LogoutView.as_view(), name='logout'),  # <-- Add this line
    path('', include(router.urls)),
    path('users/<int:pk>/deactivate/', UserViewSet.as_view({'post': 'deactivate'}), name='user-deactivate'),
    path('users/<int:pk>/reactivate/', UserViewSet.as_view({'post': 'reactivate'}), name='user-reactivate'),
    path('users/<int:pk>/update-photo/', UserViewSet.as_view({'post': 'update_photo'}), name='user-update-photo'),
    path('users/<int:pk>/set-mobile-verified/', UserViewSet.as_view({'post': 'set_mobile_verified'}), name='user-set-mobile-verified'),
    path('users/<int:pk>/set-email-verified/', UserViewSet.as_view({'post': 'set_email_verified'}), name='user-set-email-verified'),
    path('', include(router.urls)),
]