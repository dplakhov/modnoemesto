# -*- coding: utf-8 -*-
from apps.billing.api import CameraAccessor

from apps.social.documents import User
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
import traceback
from django.http import HttpResponse
from django.conf import settings

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
    logger.debug('cam_view_notify request %s' % repr(request.GET.items()))

    try:
        result = CameraAccessor(request)
    except CameraAccessor.APIException, e:
        params = (-1, 0, 0)
        logger.debug('cam_view_notify api error:\n%s\n%s' % (e, traceback.format_exc()))
    except Exception, e:
        params = (-500, 0, 0)
        logger.debug('cam_view_notify error:\n%s\n%s' % (e, traceback.format_exc()))
    else:
        params = result.status, result.time, result.stream
        logger.debug('cam_view_notify response %s' % repr(params))

    if format == 'xml':
        return direct_to_template(request,
                                  'server_api/cam_view_notify.xml',
                                  { 'params': zip(('status', 'time', 'stream'), params) },
                                  mimetype='xml/plain'
                                  )
    else:
        return HttpResponse('|'.join(str(i) for i in params))
