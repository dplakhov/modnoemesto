# -*- coding: utf-8 -*-
from apps.social.documents import User
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
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
