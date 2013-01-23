# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from mongoengine.django.shortcuts import get_document_or_404

from apps.social.documents import User
from apps.friends.documents import FriendshipOffer, UserFriends


def list(request):
    return direct_to_template(request, 'friends/friend_list.html')


def friends_online(request, id):
    return direct_to_template(request, 'friends/friends_online.html',
                              dict(page_user=get_document_or_404(User, id=id)))


def friends_all(request, id):
    return direct_to_template(request, 'friends/friends_all.html',
                              dict(page_user=get_document_or_404(User, id=id)))


def add(request, id):
    user = request.user
    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.can_add(friend):
        user.friends.offers.send(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer sent'))

    return redirect('friends:list')


def remove(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.contains(friend):
        user.friends.unfriend(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend removed'))

    return redirect('friends:list')


def cancel(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_for_user(friend):
        user.friends.offers.cancel(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer cancelled'))

    return redirect('friends:list')


def reject(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.reject(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer rejected'))

    return redirect('friends:list')


def accept(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.accept(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer accepted'))

    return redirect('friends:list')


def offers_sent(request):
    return direct_to_template(request, 'friends/sent.html')