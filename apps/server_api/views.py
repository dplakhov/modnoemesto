# -*- coding: utf-8 -*-
from apps.billing.documents import AccessCamOrder
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
import traceback

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

        0 OK

        -1 BAD PARAMS
        -2 BAD STATUS
        -3 BAD TIME
        -4 BAD SESSION KEY
        -5 BAD CAMERA ID
        -500 INTERNAL ERROR
    """
    from apps.media.documents import File
    logger.debug('cam_view_notify request %s' % repr(request.GET.items()))

    def calc():
        if not request.GET:
            return -1, 0, 0
        status = request.GET.get('status', None)
        session_key = request.GET.get('session_key', None)
        camera_id = request.GET.get('camera_id', None)
        extra_time = request.GET.get('time', None)
        if not (status and session_key and camera_id):
            return -1, 0, 0
        if status not in ['connect', 'next', 'disconnect']:
            return -2, 0, 0
        if extra_time is None:
            if status != 'connect':
                return -1, 0, 0
        elif not extra_time.isdigit():
            return -3, 0, 0
        else:
            extra_time = int(extra_time)
            if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
                return -3, 0, 0
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            return -4, 0, 0
        user = User.objects(id=user_id).first()
        if not user:
            return -4, 0, 0
        camera = Camera.objects(id=camera_id).first()
        if not camera:
            return -5, 0, 0
        now = datetime.now()
        can_show, info = camera.can_show(user, now)
        if not can_show:
            if info == 'not_paid':
                time_left = camera.get_trial_view_time(session)
                if time_left > 0:
                    time_next = time_left - extra_time
                    camera.set_trial_view_time(session, time_next)
                    if time_next > 0:
                        if time_next > settings.TIME_INTERVAL_NOTIFY:
                            time_next = settings.TIME_INTERVAL_NOTIFY
                        return 0, time_next, camera.stream_name
            return 0, 0, camera.stream_name
        if not camera.is_view_paid:
            return 0, 0 if status == 'disconnect' else settings.TIME_INTERVAL_NOTIFY, camera.stream_name
        time_left, order = camera.get_show_info(user, now)
        # for enabled operator and owner
        if time_left is None:
            return 0, 0 if status == 'disconnect' else settings.TIME_INTERVAL_NOTIFY, camera.stream_name
        if order.is_packet:
            time_next = time_left.days * 60 * 60 * 24 + time_left.seconds
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
        else:
            if order.begin_date is None:
                if status != 'connect':
                    return -6, 0, 0
                order.begin_date = datetime.now()
                order.save()
            time_next = order.get_time_left(user.cash)
            if time_next == 0:
                order.set_time_at_end()
                order.save()
                return 0, 0, camera.stream_name
            if status != 'connect':
                total_cost = order.tariff.cost * extra_time
                user.cash -= total_cost
                user.save()
                order.duration += extra_time
            time_next = order.get_time_left(user.cash)
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
            if status == 'disconnect' or time_next == 0:
                order.set_time_at_end()
                order.cost = order.tariff.cost * order.duration
                order.save()
                return 0, 0, camera.stream_name
            order.save()
        if status == 'connect':
            return 0, time_next, camera.stream_name
        return 0, time_next, camera.stream_name
    try:
        params = calc()
    except Exception, e:
        params = (-500, 0, 0)
        logger.debug('cam_view_notify error %s\n%s\n\n' % (repr(e), traceback.format_exc()))
    else:
        logger.debug('cam_view_notify response %s' % repr(params))
    if format == 'xml':
        return direct_to_template(request,
                                  'server_api/cam_view_notify.xml',
                                  { 'params': zip(('status', 'time', 'stream'), params) },
                                  mimetype='xml/plain'
                                  )
    else:
        return HttpResponse('|'.join(str(i) for i in params))
