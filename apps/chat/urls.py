from django.conf.urls.defaults import *

urlpatterns = patterns('apps.chat.views',
    (r'^send/', 'send'),
    (r'^subscribe/', 'subscribe'),
    (r'^unsubscribe/', 'unsubscribe'),
)