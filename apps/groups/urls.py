# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('apps.groups.views',
       url(r'^$', 'group_list', name='group_list'),
       url(r'^my/$', 'user_group_list', name='user_group_list'),
       url(r'^add/$', 'group_edit', name='group_add'),

       url(r'^(?P<id>[a-f0-9]{24})/$', 'group_view', name='group_view'),
       url(r'^(?P<id>[a-f0-9]{24})/conference/$', 'group_conference', name='group_conference'),
       url(r'^(?P<id>[a-f0-9]{24})/members/$', 'member_list', name='member_list'),
       url(r'^(?P<id>[a-f0-9]{24})/members\.(?P<format>(txt|xml))$', 'api_member_list', name='api_member_list'),

       url(r'^(?P<id>[a-f0-9]{24})/message/(?P<message_id>[a-f0-9]{24})/delete/$', 'delete_message', name='delete_message'),

       url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'group_edit', name='group_edit'),
       url(r'^(?P<id>[a-f0-9]{24})/manage/$', 'members_manage', name='members_manage'),

       url(r'^can_manage/$', 'can_manage', name='can_manage'),

       url(r'^(?P<id>[a-f0-9]{24})/photo/edit/$', 'photo_edit', name='photo_edit'),

       url(r'^(?P<id>[a-f0-9]{24})/give_admin_right/(?P<user_id>[a-f0-9]{24})/$', 'give_admin_right', name='give_admin_right'),
       url(r'^(?P<id>[a-f0-9]{24})/remove_admin_right/(?P<user_id>[a-f0-9]{24})/$', 'remove_admin_right', name='remove_admin_right'),

       url(r'^(?P<id>[a-f0-9]{24})/remove_member/(?P<user_id>[a-f0-9]{24})/$', 'remove_member', name='remove_member'),

       url(r'^(?P<id>[a-f0-9]{24})/join/$', 'group_join', name='group_join'),
       url(r'^(?P<id>[a-f0-9]{24})/join/(?P<user_id>[a-f0-9]{24})/$', 'group_join_user', name='group_join_user'),

       url(r'^(?P<id>[a-f0-9]{24})/leave/$', 'group_leave', name='group_leave'),
       url(r'^(?P<id>[a-f0-9]{24})/leave/(?P<user_id>[a-f0-9]{24})/$', 'group_leave_user', name='group_leave_user'),

       url(r'^(?P<id>[a-f0-9]{24})/invite/$', 'send_friends_invite', name='send_friends_invite'),
       url(r'^(?P<user_id>[a-f0-9]{24})/invites/$', 'send_my_invites_to_user', name='send_my_invites_to_user'),
       url(r'^(?P<id>[a-f0-9]{24})/invite/(?P<user_id>[a-f0-9]{24})/$', 'send_invite', name='send_invite'),
       url(r'^(?P<id>[a-f0-9]{24})/invite/(?P<user_id>[a-f0-9]{24})/cancel/$', 'cancel_invite', name='cancel_invite'),
       url(r'^(?P<id>[a-f0-9]{24})/invite/take/$', 'invite_take', name='invite_take'),
       url(r'^(?P<id>[a-f0-9]{24})/invite/refuse/$', 'invite_refuse', name='invite_refuse'),

       url(r'^(?P<id>[a-f0-9]{24})/request/cancel/$', 'cancel_request', name='cancel_request'),
       url(r'^(?P<id>[a-f0-9]{24})/request/take/$', 'request_take', name='request_take'),
       url(r'^(?P<id>[a-f0-9]{24})/request/refuse/$', 'request_refuse', name='request_refuse'),

       url(r'^themes/$', 'theme_list', name='theme_list'),
       url(r'^themes/add/$', 'theme_edit', name='theme_add'),
       url(r'^themes/(?P<id>[a-f0-9]{24})/edit/$', 'theme_edit', name='theme_edit'),
       url(r'^themes/(?P<id>[a-f0-9]{24})/delete/$', 'theme_delete', name='theme_delete'),

       url(r'^types/$', 'type_list', name='type_list'),
       url(r'^types/add/$', 'type_edit', name='type_add'),
       url(r'^types/(?P<id>[a-f0-9]{24})/edit/$', 'type_edit', name='type_edit'),
       url(r'^types/(?P<id>[a-f0-9]{24})/delete/$', 'type_delete', name='type_delete'),

)
