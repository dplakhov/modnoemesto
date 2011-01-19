# -*- encoding: UTF-8 -*-

from datetime import datetime
from BeautifulSoup import BeautifulSoup

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.conf import settings

from apps.chat.models import ChatStorage, Message
from apps.social.documents import User

def clean_message(message):
    soup = BeautifulSoup(message)
    message = ''.join(soup.findAll(text=True))
    words = message.split(' ')

    if len(words) >= 500:
        words = words[:500]
        message = ' '.join(words)

    return message



@login_required
def send(request):
    chat_id = request.POST.get("chat_id", "")
    message = request.POST.get("message", "")
    message = clean_message(message)

    storage = ChatStorage(chat_id)
    message = Message(request.user.pk, message)
    storage.put(message)
    return HttpResponse('')

@login_required
def sync(request):
    chat_id = request.POST.get('id')
    storage = ChatStorage(chat_id)

    return HttpResponse(storage.all_json())

@login_required
def receive(request):
    if request.method != 'POST':
        raise Http404
    post = request.POST

    if not post.get('chat_id', None) or not post.get('offset', None):
        raise Http404

    try:
        chat_id = post['chat_id']
    except:
        raise Http404

    storage = ChatStorage(chat_id)
    storage.set_user_online(request.user.pk)

    offset = post['offset']

    if offset == u'0':
        offset = datetime(2000, 01, 01).strftime(settings.CHAT_MESSAGE_DATE_FORMAT)

    storage = ChatStorage(chat_id)
    json_data = storage.get_by_offset_json(offset)

    return HttpResponse(json_data)


@login_required
def join(request):
    chat_id = request.POST.get("chat_id", "")

    storage = ChatStorage(chat_id)
    user = User.objects.get(pk=request.user.pk)
    text = u"%s входит в чат." % user.get_full_name()
    message = Message(request.user.pk, text, type=Message.TYPE_SYSTEM)
    storage.put(message)
    return HttpResponse('')


@login_required
def leave(request):
    chat_id = request.POST.get("chat_id", "")

    storage = ChatStorage(chat_id)
    storage.set_user_offline(request.user.pk)
    return HttpResponse('')


@login_required
def index(request):
    messages = []
    return render_to_response('chat/chat.html',
                              {
                               'messages': messages
                              },
                              context_instance=RequestContext(request))


def jsonify(object, fields=None, to_dict=False):
    '''Simple convert model to json'''
    try:
        import json
    except:
        import django.utils.simplejson as json

    out = []
    if type(object) not in [dict, list, tuple] :
        for i in object:
            tmp = {}
            if fields:
                for field in fields:
                    tmp[field] = unicode(i.__getattribute__(field))
            else:
                for attr, value in i.__dict__.iteritems():
                    tmp[attr] = value
            out.append(tmp)
    else:
        out = object
    if to_dict:
        return out
    else:
        return json.dumps(out)
