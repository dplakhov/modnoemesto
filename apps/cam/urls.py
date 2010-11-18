# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.cam.views',
    url(r'^$', 'cam_list', name='cam_list'),
    url(r'^add/$', 'cam_edit', name='cam_add'),

    url(r'^(?P<id>[a-f0-9]{24})/$', 'cam_view', name='cam_view'),

    url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'cam_edit', name='cam_edit'),

    #url(r'^(?P<id>[a-f0-9]{24})/enable/$', 'cam_edit', name='cam_edit'),


    url(r'^types/$', 'type_list', name='type_list'),
    url(r'^types/add/$', 'type_edit', name='type_add'),
    url(r'^types/(?P<id>[a-f0-9]{24})/$', 'type_edit', name='type_edit'),
    url(r'^types/(?P<id>[a-f0-9]{24})/delete/$', 'type_delete', name='type_delete'),

)