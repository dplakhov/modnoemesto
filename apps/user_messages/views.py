# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

from mongoengine.django.shortcuts import get_document_or_404

from .forms import MessageTextForm

from .documents import Message
from apps.social.documents import User

#@login_required
def send_message(request, user_id):
    
    from apps.social.documents import User

    if user_id == request.user.id:
        raise Http404()
    msgform = MessageTextForm(request.POST or None)
    recipient = get_document_or_404(User, id=user_id)
    if msgform.is_valid():
        text = msgform.data['text']
        Message.send(request.user, recipient, text)
        return redirect('user_messages:view_inbox')
    else:
        #@todo: use separate form and screen to handle each situation
        return direct_to_template(request, 'user_messages/write_message.html',
                              { 'page_user': recipient, 'msgform': msgform })


#@login_required
def view_inbox(request):
    #@todo: pagination
    #@todo: partial data fetching
    messages = request.user.messages.incoming[0:10]
    return direct_to_template(request, 'user_messages/inbox.html',
                              { 'msgs': messages })


#@login_required
def view_sent(request):
    #@todo: pagination
    #@todo: partial data fetching
    messages = request.user.messages.sent[0:10]
    return direct_to_template(request, 'user_messages/sent.html',
                              { 'msgs': messages })


def _message_acl_check(message, user):
    if not message.is_sender(user) and not message.is_recipient(user):
        raise Http404()


#@login_required
def view_message(request, message_id):
    from apps.social.documents import User
    message = get_document_or_404(Message, id=message_id)
    user = request.user
    _message_acl_check(message, user)


    if message.recipient.id == request.user.id and not message.is_read:
        message.set_readed()

    return direct_to_template(request, 'user_messages/message.html',
                              { 'msg': message })


#@login_required
def delete_message(request, message_id):
    from apps.social.documents import User
    message = get_document_or_404(Message, id=message_id)
    user = request.user
    _message_acl_check(message, user)

    message.set_user_delete(request.user)
    if message.is_sender(user):
        return redirect('user_messages:view_sent')
    elif message.is_recipient(user):
        return redirect('user_messages:view_inbox')

