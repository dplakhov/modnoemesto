# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.admin_blog.views',
    url(r'^$', 'list', name='list'),

    url(r'^(?P<id>[a-f0-9]{24})/$', 'view', name='view'),

    url(r'^add/$', 'edit', name='add'),
    url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'edit', name='edit'),

    url(r'^(?P<id>[a-f0-9]{24})/delete/$', 'delete', name='delete'),
)