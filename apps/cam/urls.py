# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from django.conf import settings

urlpatterns = patterns('apps.cam.views',
    url(r'^$', 'cam_list', name='cam_list'),
    url(r'add/$', 'cam_add', name='cam_add'),

    url(r'types/$', 'type_list', name='type_list'),
    url(r'types/add/$', 'type_add', name='type_add'),



)