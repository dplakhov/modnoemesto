# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.news.views',
   url(r'^add/$', 'news_add', name='news_add'),
)