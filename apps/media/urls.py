# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.media.views',
   url(r'^(?P<code>[a-f0-9]{12})/$', 'file_view', name='file_view'),
)