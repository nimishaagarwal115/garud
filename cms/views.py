from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from .models import Inquiry

def inquiry_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        # Save to DB
        inquiry = Inquiry.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )
        # Send email
        subject = 'New Inquiry Received'
        body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message}"
        send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        return HttpResponse('<h2>Thank you for your inquiry!</h2>')
    return HttpResponse('<h2>Invalid request.</h2>', status=400)
