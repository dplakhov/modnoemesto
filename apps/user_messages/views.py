# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.views.generic.simple import direct_to_template
from django.shortcuts import redirect

from mongoengine.django.shortcuts import get_document_or_404

from apps.social.forms import MessageTextForm

from .documents import Message

@login_required
def send_message(request, user_id):
    
    from apps.social.documents import Account

    if user_id == request.user.id:
        raise Http404()
    msgform = MessageTextForm(request.POST or None)
    recipient = get_document_or_404(Account, id=user_id)
    if msgform.is_valid():
        text = msgform.data['text']
        request.user.send_message(text, recipient)
        return redirect('social:home')
    else:
        #@todo: use separate form and screen to handle each situation
        return direct_to_template(request, 'social/user.html',
                              { 'page_user': recipient, 'msgform': msgform })


@login_required
def view_inbox(request):
    #@todo: pagination
    #@todo: partial data fetching
    messages = reversed(request.user.msg_inbox[-10:])
    return direct_to_template(request, 'user_messages/inbox.html',
                              { 'msgs': messages })


@login_required
def view_sent(request):
    #@todo: pagination
    #@todo: partial data fetching
    messages = reversed(request.user.msg_sent[-10:])
    return direct_to_template(request, 'user_messages/sent.html',
                              { 'msgs': messages })


@login_required
def view_message(request, message_id):
    from apps.social.documents import Account
    message = get_document_or_404(Message, id=message_id, userlist=request.user)
    if message.recipient == request.user and not message.is_read:
        Account.objects(id=request.user.id).update_one(dec__unread_msg_count=1)
        Message.objects(id=message.id).update_one(set__is_read=True)
    return direct_to_template(request, 'user_messages/message.html',
                              { 'msg': message })


@login_required
def delete_message(request, message_id):
    message = get_document_or_404(Message, id=message_id, userlist=request.user)
    message.delete_from(request.user)
    return redirect('view_inbox:view_inbox')

