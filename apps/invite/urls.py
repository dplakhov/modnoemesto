# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.invite.views',
   url(r'^send/$', 'invite_send', name='invite_send'),
   url(r'^(?P<invite_id>[a-f0-9]{24})/$', 'invite', name='invite'),
)
  