# -*- coding: utf-8 -*-
from datetime import datetime
from apps.social.documents import User
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse
from django.core import serializers


def call_user(request, id):
    recipient = User.objects(id=id).first()
    if not recipient:
        return HttpResponse('NOT FOUND')
    if not recipient.is_online():
        return HttpResponse('OFFLINE')
    last_view = cache.get('LAST_VIEW_%s' % recipient.id, 1, None)
    if last_view is None:
        cache.set('CALL_EVENT_%s' % recipient.id, request.user.id, datetime.now() - settings.VIDEO_CALL_INTERVAL_UPDATE)
        return HttpResponse('WHITE')
    return HttpResponse('OK')


def check_calls(request):
    def wrapper():
        sender = cache.get('CALL_EVENT_%s' % request.user.id, None)
        if sender is None:
            return {}
        sender = User.objects(id=sender).first()
        if not sender:
            return {}
        return { 'id': sender.id, 'name': sender }
    data = serializers.serialize('json', wrapper())
    return HttpResponse(data)


def set_last_view(request):
    cache.set('LAST_VIEW_%s' % request.user.id, 1, settings.VIDEO_CALL_INTERVAL_UPDATE.seconds)
    return HttpResponse('OK')