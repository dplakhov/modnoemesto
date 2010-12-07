# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.social.views',
   url(r'^$', 'index', name='index'),
   url(r'^start/$', 'start', name='start'),
   url(r'^stop/$', 'stop', name='stop'),
   url(r'^home/$', 'home', name='home'),
   url(r'^home/edit/$', 'profile_edit', name='profile_edit'),

   url(r'^login/$', 'about', name='login'),
   url(r'^logout/$', 'logout', name='logout'),
   url(r'^register/$', 'about', name='register'),
   url(r'^activation/(?P<code>[a-f0-9]{12})/$', 'activation',
       name='activation'),

   url(r'^users/(?P<user_id>[a-f0-9]{24})/$', 'user', name='user'),

   url(r'^avatar/(?P<user_id>[a-f0-9]{24})/(?P<format>%s)/$' %
       '|'.join(['%dx%d' % (w, h) for (w, h) in settings.AVATAR_SIZES ]),

       'avatar', name='avatar'),

   url(r'^profile/$', 'profile_edit', name='profile_edit'),
   url(r'^profile/avatar/$', 'avatar_edit', name='avatar_edit'),

)
