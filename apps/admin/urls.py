# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.admin.views',
    url(r'^statistic/$', 'statistic', name='statistic'),
    url(r'^users/$', 'user_list', name='user_list'),
)