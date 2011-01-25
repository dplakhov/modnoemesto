# -*- coding: utf-8 -*-
from apps.billing.documents import AccessCamOrder
from apps.cam.documents import Camera
from apps.social.documents import User
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
from datetime import datetime
from django.http import HttpResponse
import urllib
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.utils.importlib import import_module

import logging
logger = logging.getLogger('server_api')

STREAMED_USERS_DATABASE = 'streamed_users'
STREAMED_USERS_SET = 'streamed_users'


from decorators import server_only_access


client = redis.Redis(**settings.REDIS_DATABASES[STREAMED_USERS_DATABASE])


def _get_users(request):
    users = request.POST.get('users', '')
    return users.split(',')

def _append_online(users):
    for user in users:
        client.sadd(STREAMED_USERS_SET, user)

@server_only_access()
def notify_online(request):
    users = _get_users(request)
    if users:
        _append_online(users)

    return HttpResponse()

@server_only_access()
def notify_offline(request):
    users = _get_users(request)

    for user in users:
        client.srem(STREAMED_USERS_SET, user)

    return HttpResponse()

@server_only_access()
def notify_reset(request):
    while client.spop(STREAMED_USERS_SET):
        pass

    users = _get_users(request)
    if users:
        _append_online(users)

    return HttpResponse()

#@server_only_access()
def friend_list(request, id, format, state):
    logger.debug('friend_list request %s' % id)

    user = get_document_or_404(User, id=id)
    mimetypes = dict(
            txt='text/plain',
            xml='xml/plain',
                     )
    if state == 'all':
        _list = user.friends.list
    elif state == 'online':
        _list = user.friends_online

    else:
        raise NotImplementedError()
    _list = list(_list)
    _list.insert(0, user)
    return direct_to_template(request,
                              'server_api/user_friend_list.%s' % format,
                              dict(list=_list),
                              mimetype=mimetypes[format]
                              )


def cam_view_notify(request):
    def calc():
        action = request.GET.get('action', None)
        session_key = request.GET.get('session_key', None)
        camera_id = request.GET.get('camera_id', None)
        extra_time = request.GET.get('time', None)
        if not (action and session_key and camera_id and extra_time is not None):
            return 'BAD PARAMS (action, session_key, camera_id, time)', -1
        if not extra_time.isdigit():
            return 'BAD TIME', -2
        extra_time = int(extra_time)
        if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
            return 'BAD TIME', -2
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            return 'BAD SESSION KEY', -3
        user = User.objects(id=user_id).first()
        if not user:
            return 'BAD SESSION KEY', -3
        camera = Camera.objects(id=camera_id).first()
        if not camera:
            return 'BAD CAMERA ID', -4
        now = datetime.now()
        can_show = camera.can_show(camera.owner, user, now)
        if not can_show:
            return 'OK', 0, 0
        if not camera.is_view_paid:
            return 'OK', 0, settings.TIME_INTERVAL_NOTIFY
        time_left, order = camera.get_show_info(user, now)
        if order.is_packet:
            time_next = time_left.days * 60 * 60 * 24 + time_left.seconds
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
            return 'OK', 0, time_next
        else:
            total_cost = order.tariff.cost * (settings.TIME_INTERVAL_NOTIFY - extra_time)
            user.cash -= total_cost
            user.save()
            time_next = order.get_time_left(user.cash)
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
            order.duration += time_next
            if action == 'disconnect' or time_next == 0:
                order.set_time_at_end()
                order.save()
                return 'OK', 0, 0
            order.save()
            return 'OK', 0, time_next
    return HttpResponse('&%s' % urllib.urlencode(zip(('info', 'status', 'time'),
                                                     calc(),
                                                     )))
