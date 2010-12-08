# -*- coding: utf-8 -*-


from django.conf.urls.defaults import patterns, url

from django.conf import settings

urlpatterns = patterns('apps.media_library.views',
   url(r'^video/$', 'video_index', name='video_index'),
   url(r'^audio/$', 'audio_index', name='audio_index'),

   url(r'^image/$', 'image_index', name='image_index'),
   url(r'^image/add/$', 'image_add', name='image_add'),
   url(r'^image/(?P<id>[a-f0-9]{24})/delete/$', 'image_delete', name='image_delete'),
)