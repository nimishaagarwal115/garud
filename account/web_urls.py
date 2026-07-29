from django.urls import path
from .web_views import (
    register,
    login_view,
    profile,
    logout_view,
    set_mpin_view,
)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('set-mpin/', set_mpin_view, name='set_mpin'),
]