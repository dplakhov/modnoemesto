# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('apps.user_messages.views',
    url(r'^inbox/$', 'view_inbox', name='view_inbox'),
    url(r'^sent/$', 'view_sent', name='view_sent'),
    url(r'^(?P<message_id>[a-f0-9]{24})/$', 'view_message',
        name='view_message'),
    url(r'^(?P<message_id>[a-f0-9]{24})/delete/$', 'delete_message',
        name='delete_message'),
    url(r'^user/(?P<user_id>[a-f0-9]{24})/send/$', 'send_message',
        name='send_message'),
    )
