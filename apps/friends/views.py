# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect

from mongoengine.django.shortcuts import get_document_or_404

from apps.social.documents import User


@login_required
def list(request):
    return direct_to_template(request, 'friends/friend_list.html')

@login_required
def add(request, id):
    user = request.user
    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.can_add(friend):
        user.friends.offers.send(friend)

    return redirect('friends:list')


@login_required
def remove(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.contains(friend):
        user.friends.remove(friend)

    return redirect('friends:list')


@login_required
def accept(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.accept(friend)

    return redirect('friends:list')

@login_required
def reject(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.reject(friend)

    return redirect('friends:list')

@login_required
def offers_inbox(request):
    return direct_to_template(request, 'friends/inbox.html')

@login_required
def offers_sent(request):
    return direct_to_template(request, 'friends/sent.html')
