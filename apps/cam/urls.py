# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from .constants import AVAILABLE_COMMANDS
from django.conf import settings

urlpatterns = patterns('apps.cam.views',
    url(r'^$', 'cam_list', name='cam_list'),
    url(r'^add/$', 'cam_edit', name='cam_add'),
    url(r'^bookmarks/$', 'cam_bookmarks', name='cam_bookmarks'),
    url(r'^bookmarks/(?P<id>[a-f0-9]{24})/add/$', 'cam_bookmark_add', name='cam_bookmark_add'),
    url(r'^bookmarks/(?P<id>[a-f0-9]{24})/delete/$', 'cam_bookmark_delete', name='cam_bookmark_delete'),

    url(r'^(?P<id>[a-f0-9]{24})/$', 'cam_view', name='cam_view'),
    url(r'^(?P<id>[a-f0-9]{24})/edit/$', 'cam_edit', name='cam_edit'),
    url(r'^(?P<id>[a-f0-9]{24})/manage/(%s)/$' % '|'.join(AVAILABLE_COMMANDS),
        'cam_manage', name='cam_manage'),

    #url(r'^(?P<id>[a-f0-9]{24})/enable/$', 'cam_edit', name='cam_edit'),

    url(r'^screen/$', 'screen_edit', name='screen_edit'),
    url(r'^(?P<id>[a-f0-9]{24})/screen/edit/$', 'screen_edit', name='screen_edit'),

    url(r'^types/$', 'type_list', name='type_list'),
    url(r'^types/add/$', 'type_edit', name='type_add'),
    url(r'^types/(?P<id>[a-f0-9]{24})/$', 'type_edit', name='type_edit'),
    url(r'^types/(?P<id>[a-f0-9]{24})/delete/$', 'type_delete', name='type_delete'),

    url(r'^tags/$', 'tag_list', name='tag_list'),
    url(r'^tags/add/$', 'tag_edit', name='tag_add'),
    url(r'^tags/(?P<id>[a-f0-9]{24})/$', 'tag_edit', name='tag_edit'),
    url(r'^tags/(?P<id>[a-f0-9]{24})/delete/$', 'tag_delete', name='tag_delete'),

    url(r'^(?P<id>[a-f0-9]{24})/inc_view_count/$', 'inc_view_count', name='inc_view_count'),
)