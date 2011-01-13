# -*- encoding: UTF-8 -*-

from datetime import datetime

from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import User 

from apps.chat.models import Chat, ChatStorage, Message, MAX_ITEMS

from BeautifulSoup import BeautifulSoup

@login_required
def send(request):
    message = request.POST.get("message", "")
    soup = BeautifulSoup(message)
    message = ''.join(soup.findAll(text=True))
    words = message.split(' ')     
    if len(words) >= 500:
        words = words[:500]
        message = ' '.join(words)
         
    
    chat_id = request.POST.get("chat_id", "")
    
    storage = ChatStorage(chat_id)
    message = Message(request.user.pk, message)
    storage.put(message)
    return HttpResponse('')

def mock_messages(request):
    chat_id = request.POST.get('id')
    user_id = request.user.pk
    storage = ChatStorage(chat_id)
    
    text = "test message %d"
    messages = []
    for i in range(MAX_ITEMS + 7):
        message = Message(user_id, text % i)
        messages.append(message)
        storage.put(message)    
    

@login_required
def sync(request):
    chat_id = request.POST.get('id')
    storage = ChatStorage(chat_id)
    
    #mock_messages(request)
    
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

    from models import DATE_FORMAT
    offset = post['offset']

    if offset == u'0':
        offset = datetime(2000, 01, 01).strftime(DATE_FORMAT)

    storage = ChatStorage(chat_id)
    json_data = storage.get_by_offset_json(offset)
    
    
    
    return HttpResponse(json_data)


@login_required
def join(request):
    p = request.POST
    return HttpResponse('')


@login_required
def leave(request):
    p = request.POST
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
    if type(object) not in [dict,list,tuple] :
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
