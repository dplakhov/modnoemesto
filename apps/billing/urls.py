# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.billing.views',
    url(r'^camera/(?P<id>[a-f0-9]{24})/access/$', 'get_access_to_camera', name='get_access_to_camera'),
    url(r'^purse/$', 'purse', name='purse'),
    url(r'^tariffs/$', 'tariff_list', name='tariff_list'),
    url(r'^tariffs/add/$', 'tariff_edit', name='tariff_add'),
    url(r'^tariffs/(?P<id>[a-f0-9]{24})/$', 'tariff_edit', name='tariff_edit'),
    url(r'^tariffs/(?P<id>[a-f0-9]{24})/delete/$', 'tariff_delete', name='tariff_delete'),
)