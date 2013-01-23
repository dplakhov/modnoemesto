# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.media.views',
   url(r'^(?P<file_id>[a-f0-9]{24})/(?P<transformation_name>[\w\.]+)$',
       'file_view', name='file_view'),
   url(r'^(?P<transformation_name>[\w\.]+)$', 'file_view', name='file_view'),
)