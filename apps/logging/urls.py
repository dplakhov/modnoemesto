# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.logging.views',
       url(r'^$', 'log_list', name='log_list'),
)
