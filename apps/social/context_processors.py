
from django.conf import settings

def site_domain(request):
    return { 'SITE_DOMAIN': settings.SITE_DOMAIN }
