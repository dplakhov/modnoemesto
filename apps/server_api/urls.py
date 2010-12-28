# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from .constants import AVAILABLE_COMMANDS
from django.conf import settings

urlpatterns = patterns('server_api.cam.views',
    url(r'^notify/online/$', 'notify_online', name='notify_online'),
    url(r'^notify/offline/$', 'notify_offline', name='notify_offline'),
    url(r'^notify/reset/$', 'notify_reset', name='notify_reset'),
)