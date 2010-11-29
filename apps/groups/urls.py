# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.groups.views',
       url(r'^$', 'group_list', name='group_list'),
       url(r'^add/$', 'group_add', name='group_add'),
       url(r'^(?P<id>[a-f0-9]{24})/$', 'group_view', name='group_view'),
       url(r'^(?P<id>[a-f0-9]{24})/join/$', 'group_join', name='group_join'),
       url(r'^(?P<id>[a-f0-9]{24})/leave/$', 'group_leave', name='group_leave'),

)