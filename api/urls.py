from django.urls import path
from .views import TTSView, STTView, TranslateView

urlpatterns = [
    path('tts/', TTSView.as_view(), name='tts'),
    path('stt/', STTView.as_view(), name='stt'),
    path('translate/', TranslateView.as_view(), name='translate'),
]
