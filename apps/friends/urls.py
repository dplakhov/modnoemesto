# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.friends.views',
       url(r'^$', 'list', name='list'),
       url(r'^(?P<id>[a-f0-9]{24})/online/$', 'friends_online', name='friends_online'),
       url(r'^(?P<id>[a-f0-9]{24})/all/$', 'friends_all', name='friends_all'),

       url(r'^offers/sent/$', 'offers_sent', name='offers_sent'),

       url(r'^(?P<id>[a-f0-9]{24})/add/$', 'add', name='add'),
       url(r'^(?P<id>[a-f0-9]{24})/remove/$', 'remove', name='remove'),

       url(r'^(?P<id>[a-f0-9]{24})/accept/$', 'accept', name='accept'),
       url(r'^(?P<id>[a-f0-9]{24})/reject/$', 'reject', name='reject'),

       url(r'^(?P<id>[a-f0-9]{24})/cancel/$', 'cancel', name='cancel'),
)
