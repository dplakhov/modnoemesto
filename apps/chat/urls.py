from django.conf.urls.defaults import *

urlpatterns = patterns('apps.chat.views',
    url(r'^$', 'index'),
    url(r'^send/$', 'send'),
    url(r'^receive/$', 'receive'),
    url(r'^sync/$', 'sync'),

    url(r'^join/$', 'join'),
    url(r'^leave/$', 'leave'),
)