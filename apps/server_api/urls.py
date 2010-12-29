# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('apps.server_api.views',
    url(r'^notify/online/$', 'notify_online', name='notify_online'),
    url(r'^notify/offline/$', 'notify_offline', name='notify_offline'),
    url(r'^notify/reset/$', 'notify_reset', name='notify_reset'),

    url(r'^user/(?P<id>[a-f0-9]{24})/friends/(?P<state>(online|all))\.(?P<format>(txt|xml))$',
        'friend_list', name='friend_list'),

)