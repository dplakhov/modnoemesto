# -*- coding: utf-8 -*-
from apps.billing.documents import AccessCamOrder
from apps.social.documents import User
from django.views.generic.simple import direct_to_template
from mongoengine.django.shortcuts import get_document_or_404

import redis
from django.http import HttpResponse
import urllib
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.utils.importlib import import_module


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

@server_only_access()
def friend_list(request, id, format, state):
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

    return direct_to_template(request,
                              'server_api/user_friend_list.%s' % format,
                              dict(list=_list),
                              mimetype=mimetypes[format]
                              )


def cam_view_notify(request):
    def calc():
        status = request.GET.get('status', None)
        session_key = request.GET.get('session_key', None)
        order_id = request.GET.get('order_id', None)
        extra_time = request.GET.get('time', None)
        if not (status and session_key and order_id and extra_time):
            return 'BAD PARAMS', -1
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
        order = AccessCamOrder.objects(id=order_id).first()
        if not order:
            return 'DOES NOT EXIST ORDER', -4
        if order.user != user:
            return 'BAD USER', -5
        if order.end_date or order.tariff.is_packet:
            return 'BAD ORDER', -6
        total_cost = order.tariff.cost * (settings.TIME_INTERVAL_NOTIFY - extra_time)
        user.cash -= total_cost
        user.save()
        time_left = order.get_time_left(user.cash)
        if time_left > settings.TIME_INTERVAL_NOTIFY:
            time_left = settings.TIME_INTERVAL_NOTIFY
        order.duration += time_left
        if status == 'disconnect':
            order.set_end_time()
            order.save()
            return 'OK', 0, 0
        return 'OK', 0, time_left
    result = calc()
    result = ["%s=%s" % (k, urllib.quote(str(v))) for k, v in zip(('info', 'status', 'cash'), result)]
    return HttpResponse('&%s' % ('&'.join(result)))