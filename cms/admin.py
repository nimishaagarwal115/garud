from django.contrib import admin
from .models import Inquiry as inquiryModel


admin.site.register(inquiryModel)  # Register your inquiry model here