from django.urls import path
from .views import ScheduleNotificationView, test_email_template, NotificationLogView
from .views import SellerNotificationListView, mark_as_read, mark_all_as_read

urlpatterns = [
    path('schedule/', ScheduleNotificationView.as_view(), name='schedule-notification'),
    path("test-email-template/", test_email_template, name="test_email_template"),
    path('logs/', NotificationLogView.as_view(), name='notification-log-list'),
    path('logs/<int:pk>/', NotificationLogView.as_view(), name='notification-log-detail'),
    path('seller/', SellerNotificationListView.as_view(), name='seller_notifications'),
    path('seller/mark-read/<int:pk>/', mark_as_read, name='mark_notification_read'),
    path('seller/mark-all-read/', mark_all_as_read, name='mark_all_notifications_read'),
]