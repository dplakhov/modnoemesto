
from django.conf import settings

def call_settings(request):
    return { 'VIDEO_CALL_INTERVAL_UPDATE': settings.VIDEO_CALL_INTERVAL_UPDATE }
