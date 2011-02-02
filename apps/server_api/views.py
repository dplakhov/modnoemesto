# -*- coding: utf-8 -*-
from apps.billing.api import CameraAccessor
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
import traceback
from django.http import HttpResponse
from django.conf import settings
from apps.cam.documents import Camera
from django.contrib.auth import SESSION_KEY
from django.utils.importlib import import_module
from apps.social.documents import User
from apps.video_call.views import call_user as ajax_call_user
from time import time

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

def log(request):
    level = request.REQUEST.get('level', None)
    message = request.REQUEST.get('message', None)
    if level is not None and message is not None:
        f = { 'critical': logger.critical,
              'debug': logger.debug,
              'error': logger.error,
              'exception': logger.exception,
              'fatal': logger.fatal,
              'info': logger.info,
              'warning': logger.warning }.get(level.lower())
        if f:
            f('%s\n%s' % (request.META['REMOTE_ADDR'], message))
        return HttpResponse('STATUS=SUCCESS')
    return HttpResponse('STATUS=FAIL')


def cam_view_notify(request, format):
    """ API:
        ?session_key=<Fx24>&camera_id=<Fx24>&status=connect
        ?session_key=<Fx24>&camera_id=<Fx24>&status=next&time=<sec>
        ?session_key=<Fx24>&camera_id=<Fx24>&status=disconnect&time=<sec>

        0 OK

        -1 BAD PARAMS
        -500 INTERNAL ERROR
    """

    from apps.media.documents import File

    request_id = time()
    def log_debug(text):
        logger.debug('%s\n%s' % (request_id, text))

    log_debug('cam_view_notify request %s' % repr(request.GET.items()))

    try:
        if not request.GET:
            raise CameraAccessor.APIException("Bad params")
        status = request.GET.get('status', None)
        session_key = request.GET.get('session_key', None)
        camera_id = request.GET.get('camera_id', None)
        if not (status and session_key and camera_id):
            raise CameraAccessor.APIException("Bad params")
        extra_time = request.GET.get('time', None)
        if extra_time is None:
            return
        if not extra_time.isdigit():
            raise CameraAccessor.APIException("Time must by a digit")
        extra_time = int(extra_time)
        if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
            raise CameraAccessor.APIException("Bad time interval")

        # extract data from session
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            raise CameraAccessor.APIException("Need user_id")
        user = User.objects(id=user_id).first()
        if not user:
            raise CameraAccessor.APIException("Bad user_id")
        camera = Camera.objects(id=camera_id).first()
        if not camera:
            raise CameraAccessor.APIException("Can`t found camera by camera_id")

        result = CameraAccessor(status, user, camera, session, extra_time)
    except CameraAccessor.APIException, e:
        params = (-1, 0, 0)
        log_debug('cam_view_notify api error:\n%s\n%s' % (e, traceback.format_exc()))
    except Exception, e:
        params = (-500, 0, 0)
        log_debug('cam_view_notify error:\n%s\n%s' % (e, traceback.format_exc()))
    else:
        params = result.status, result.time, result.stream
    log_debug('cam_view_notify response %s' % repr(params))

    if format == 'xml':
        return direct_to_template(request,
                                  'server_api/cam_view_notify.xml',
                                  { 'params': zip(('status', 'time', 'stream'), params) },
                                  mimetype='xml/plain'
                                  )
    else:
        return HttpResponse('|'.join(str(i) for i in params))


def call_user(request, id):
    session_key = request.GET.get('session_key', None)
    if not session_key:
        return HttpResponse('Need session_key')
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore(session_key)
    user_id = session.get(SESSION_KEY, None)
    if not user_id:
        return HttpResponse('Bad session_key')
    user = User.objects(id=user_id).first()
    if not user:
        return HttpResponse('Can`t find request user')
    return ajax_call_user(request, id, user.id)
