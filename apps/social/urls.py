# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from django.conf import settings

urlpatterns = patterns('apps.social.views',
   url(r'^$', 'index', name='index'),
   url(r'^home/$', 'home', name='home'),
   url(r'^messages/inbox/$', 'view_inbox', name='view_inbox'),
   url(r'^messages/sent/$', 'view_sent', name='view_sent'),
   url(r'^messages/(?P<message_id>[a-f0-9]{24})/$', 'view_message',
       name='view_message'),
   url(r'^messages/(?P<message_id>[a-f0-9]{24})/delete/$', 'delete_message',
       name='delete_message'),

   url(r'^login/$', 'login', name='login'),
   url(r'^logout/$', 'logout', name='logout'),
   url(r'^register/$', 'register', name='register'),
   url(r'^activation/(?P<code>[a-f0-9]{12})/$', 'activation',
       name='activation'),
   url(r'^users/(?P<user_id>[a-f0-9]{24})/$', 'user', name='user'),
   url(r'^users/(?P<user_id>[a-f0-9]{24})/send_message/$', 'send_message',
       name='send_message'),
   url(r'^users/(?P<user_id>[a-f0-9]{24})/friend/$', 'friend', name='friend'),
   url(r'^users/(?P<user_id>[a-f0-9]{24})/unfriend/$', 'unfriend',
       name='unfriend'),

   url(r'^avatar/(?P<user_id>[a-f0-9]{24})/(?P<format>%s)/$' %
       '|'.join(['%dx%d' % (w, h) for (w, h) in settings.AVATAR_SIZES ]),

       'avatar', name='avatar'),

   url(r'^friendship_offers/inbox/$', 'view_fs_offers_inbox',
       name='view_fs_offers_inbox'),
   url(r'^friendship_offers/sent/$', 'view_fs_offers_sent',
       name='view_fs_offers_sent'),
   url(r'^friendship_offers/(?P<offer_id>[a-f0-9]{24})/cancel/$',
       'cancel_fs_offer', name='cancel_fs_offer'),
   url(r'^friendship_offers/(?P<offer_id>[a-f0-9]{24})/decline/$',
       'decline_fs_offer', name='decline_fs_offer'),

   url(r'^groups/$', 'group_list', name='group_list'),
   url(r'^groups/add/$', 'group_add', name='group_add'),
   url(r'^groups/(?P<id>[a-f0-9]{24})/$', 'group_view', name='group_view'),
   url(r'^groups/(?P<id>[a-f0-9]{24})/join/$', 'group_join', name='group_join'),
   url(r'^groups/(?P<id>[a-f0-9]{24})/leave/$', 'group_leave', name='group_leave'),

   url(r'^profile/$', 'profile_edit', name='profile_edit'),
   url(r'^profile/avatar/$', 'avatar_edit', name='avatar_edit'),

)
