# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.video_call.views',
   url(r'^call_user/(?P<id>[a-f0-9]{24})/$', 'call_user', name='call_user'),
   url(r'^check_calls/$', 'check_calls', name='check_calls'),
   url(r'^set_last_view/$', 'set_last_view', name='set_last_view'),
)
