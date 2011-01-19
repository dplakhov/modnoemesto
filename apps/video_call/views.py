# -*- coding: utf-8 -*-
from apps.social.documents import User
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse


def call_user(request, id):
    recipient = User.objects(id=id).first()
    if not recipient:
        return HttpResponse('NOT FOUND')
    if not recipient.is_online():
        return HttpResponse('OFFLINE')
    last_view = cache.get('LAST_VIEW_%s' % recipient.id, None)
    if last_view is None:
        cache.set('CALL_EVENT_%s' % recipient.id, request.user.id, settings.VIDEO_CALL_INTERVAL_UPDATE)
        return HttpResponse('WHITE')
    return HttpResponse('OK')


def check_calls(request):
    def wrapper():
        sender = cache.get('CALL_EVENT_%s' % request.user.id, None)
        if sender is None:
            return ''
        sender = User.objects(id=sender).first()
        if not sender:
            return ''
        return str(sender)
    return HttpResponse(wrapper())


def set_last_view(request):
    cache.set('LAST_VIEW_%s' % request.user.id, 1, settings.VIDEO_CALL_INTERVAL_UPDATE)
    return HttpResponse('OK')