# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.logging.views',
       url(r'^$', 'log_list', name='log_list'),
       url(r'^(?P<page>\d+)/$', 'log_list', name='log_list_page'),
       
       url(r'^(?P<level>\w+)/$', 'log_list_level', name='log_list_level'),
       url(r'^(?P<level>\w+)/(?P<page>\d+)/$', 'log_list_level', name='log_list_level_page'),
       
)