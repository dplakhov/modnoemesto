# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.groups.views',
       url(r'^$', 'group_list', name='group_list'),
       url(r'^add/$', 'group_edit', name='group_add'),
       url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'group_edit', name='group_edit'),
       url(r'^(?P<id>[a-f0-9]{24})/$', 'group_view', name='group_view'),
       url(r'^(?P<id>[a-f0-9]{24})/join/$', 'group_join', name='group_join'),
       url(r'^(?P<id>[a-f0-9]{24})/join/(?P<user_id>[a-f0-9]{24})/$', 'group_join_user', name='group_join_user'),
       url(r'^(?P<id>[a-f0-9]{24})/leave/$', 'group_leave', name='group_leave'),
       url(r'^(?P<id>[a-f0-9]{24})/leave/(?P<user_id>[a-f0-9]{24})/$', 'group_leave_user', name='group_leave_user'),
       url(r'^themes/$', 'theme_list', name='theme_list'),
       url(r'^themes/add/$', 'theme_edit', name='theme_add'),
       url(r'^themes/(?P<id>[a-f0-9]{24})/edit/$', 'theme_edit', name='theme_edit'),
       url(r'^themes/(?P<id>[a-f0-9]{24})/delete/$', 'theme_delete', name='theme_delete'),
       url(r'^types/$', 'type_list', name='type_list'),
       url(r'^types/add/$', 'type_edit', name='type_add'),
       url(r'^types/(?P<id>[a-f0-9]{24})/edit/$', 'type_edit', name='type_edit'),
       url(r'^types/(?P<id>[a-f0-9]{24})/delete/$', 'type_delete', name='type_delete'),
)