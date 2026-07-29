from django.urls import path
from . import views

urlpatterns = [
    path('inquiry/', views.inquiry_view, name='inquiry'),
]
