from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .models import ScheduledNotification, NotificationLog
from .serializers import NotificationLogSerializer

class NotificationLogPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class NotificationLogView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            log = get_object_or_404(NotificationLog, pk=pk)
            serializer = NotificationLogSerializer(log)
            return Response(serializer.data)
        logs = NotificationLog.objects.filter(recipient=request.user).order_by('-created_at')
        paginator = NotificationLogPagination()
        page = paginator.paginate_queryset(logs, request)
        serializer = NotificationLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def patch(self, request, pk=None):
        if not pk:
            return Response({"detail": "Method PATCH not allowed on list."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        log = get_object_or_404(NotificationLog, pk=pk)
        log.status = "Read"
        log.save()
        serializer = NotificationLogSerializer(log)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ScheduleNotificationView(APIView):
    def post(self, request):
        data = request.data
        notification = ScheduledNotification.objects.create(
            type=data['type'],
            subject=data.get('subject'),
            body=data['body'],
            scheduled_time=data['scheduled_time']
        )
        notification.recipients.set(data['recipients'])
        notification.save()
        return Response({"message": "Notification scheduled successfully"}, status=status.HTTP_201_CREATED)

def test_email_template(request):
    """
    View to render the email template for testing in a browser.
    """
    context = {
        "logo_url": "/static/dashboard/img/logo/logo.png",  # Replace with your actual logo path
        "static_url": "",  # Base static URL
        "year": 2025,
        "recipient_email": "piyush@technoace.in",
    }
    return render(request, "emails/base_email.html", context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import SellerNotification

class SellerNotificationListView(LoginRequiredMixin, ListView):
    model = SellerNotification
    template_name = 'seller/notifications.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        return SellerNotification.objects.filter(seller=self.request.user)


@login_required
@require_POST
def mark_as_read(request, pk):
    notification = get_object_or_404(SellerNotification, pk=pk, seller=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def mark_all_as_read(request):
    SellerNotification.objects.filter(seller=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})
