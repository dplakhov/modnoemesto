# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.friends.views',
       url(r'^$', 'friend_list', name='friend_list'),
)