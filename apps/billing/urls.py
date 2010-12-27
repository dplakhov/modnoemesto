# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *


urlpatterns = patterns('apps.billing.views',
    url(r'^camera/(?P<id>[a-f0-9]{24})/access/view/$', 'get_access_to_camera', name='get_view_access_to_camera', kwargs={'is_controlled': False}),
    url(r'^camera/(?P<id>[a-f0-9]{24})/access/manage/$', 'get_access_to_camera', name='get_manage_access_to_camera', kwargs={'is_controlled': True}),
    url(r'^purse/$', 'purse', name='purse'),
    url(r'^tariffs/$', 'tariff_list', name='tariff_list'),
    url(r'^tariffs/add/$', 'tariff_edit', name='tariff_add'),
    url(r'^tariffs/(?P<id>[a-f0-9]{24})/$', 'tariff_edit', name='tariff_edit'),
    url(r'^tariffs/(?P<id>[a-f0-9]{24})/delete/$', 'tariff_delete', name='tariff_delete'),
    url(r'^orders/$', 'order_list', name='order_list'),
    url(r'^orders/(?P<page>\d+)/$', 'order_list', name='order_list_page'),
    url(r'^access_orders/$', 'access_order_list', name='access_order_list'),
    url(r'^access_orders/(?P<page>\d+)/$', 'access_order_list', name='access_order_list_page'),
    url(r'^camera/notify/$', 'cam_view_notify', name='cam_view_notify'),
)