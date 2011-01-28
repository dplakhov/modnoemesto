# -*- coding: utf-8 -*-
from apps.cam.documents import Camera
from apps.social.documents import User
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
from datetime import datetime
from django.http import HttpResponse
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


def cam_view_notify(request, format):
    """ API:
        ?session_key=<Fx24>&camera_id=<Fx24>&status=connect
        ?session_key=<Fx24>&camera_id=<Fx24>&status=next&time=<sec>
        ?session_key=<Fx24>&camera_id=<Fx24>&status=disconnect&time=<sec>
    """
    logger.debug('cam_view_notify request %s' % repr(request.GET.items()))

    def calc():
        if not request.GET:
            return 'BAD PARAMS', -1
        status = request.GET.get('status', None)
        session_key = request.GET.get('session_key', None)
        camera_id = request.GET.get('camera_id', None)
        extra_time = request.GET.get('time', None)
        if not (status and session_key and camera_id):
            return 'BAD PARAMS', -1
        if status not in ['connect', 'next', 'disconnect']:
            return 'BAD STATUS', -2
        if extra_time is None:
            if status != 'connect':
                return 'BAD PARAMS', -1
        elif not extra_time.isdigit():
            return 'BAD TIME', -3
        else:
            extra_time = int(extra_time)
            if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
                return 'BAD TIME', -3
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            return 'BAD SESSION KEY', -4
        user = User.objects(id=user_id).first()
        if not user:
            return 'BAD SESSION KEY', -4
        camera = Camera.objects(id=camera_id).first()
        if not camera:
            return 'BAD CAMERA ID', -5
        now = datetime.now()
        can_show = camera.can_show(user, now)
        if not can_show:
            return 'OK', 0, 0
        if not camera.is_view_paid:
            return 'OK', 0, 0 if status == 'disconnect' else settings.TIME_INTERVAL_NOTIFY
        time_left, order = camera.get_show_info(user, now)
        # for enabled operator and owner
        if time_left is None:
            return 'OK', 0, 0 if status == 'disconnect' else settings.TIME_INTERVAL_NOTIFY
        if order.is_packet:
            time_next = time_left.days * 60 * 60 * 24 + time_left.seconds
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
        else:
            if status != 'connect':
                total_cost = order.tariff.cost * (settings.TIME_INTERVAL_NOTIFY - extra_time)
                user.cash -= total_cost
                user.save()
                order.duration += extra_time
            time_next = order.get_time_left(user.cash)
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
            if status == 'disconnect' or time_next == 0:
                order.set_time_at_end()
                order.save()
                return 'OK', 0, 0
            order.save()
        if status == 'connect':
            return 'OK', 0, time_next, camera.stream_name
        return 'OK', 0, time_next
    try:
        params = calc()
    except Exception, e:
        params = ('INTERNAL ERROR', -500)
        logger.debug('cam_view_notify error %s' % repr(e))
    else:
        logger.debug('cam_view_notify response %s' % repr(params))
    mimetypes = dict(
            txt='text/plain',
            xml='xml/plain',
                     )
    return direct_to_template(request,
                              'server_api/cam_view_notify.%s' % format,
                              { 'params': zip(('info', 'status', 'time', 'stream'), params) },
                              mimetype=mimetypes[format]
                              )