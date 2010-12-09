# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

from mongoengine.django.shortcuts import get_document_or_404

from apps.social.documents import User
from apps.friends.documents import FriendshipOffer, UserFriends


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
        messages.add_message(request, messages.SUCCESS, _('Friend offer sent'))

    return redirect('friends:list')


@login_required
def remove(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.contains(friend):
        user.friends.unfriend(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend removed'))

    return redirect('friends:list')


@login_required
def cancel(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_for_user(friend):
        user.friends.offers.cancel(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer cancelled'))

    return redirect('friends:list')

@login_required
def reject(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.reject(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer rejected'))

    return redirect('friends:list')

@login_required
def accept(request, id):
    user = request.user

    if id == request.user.id:
        raise Http404()

    friend = get_document_or_404(User, id=id)

    if user.friends.offers.has_from_user(friend):
        user.friends.offers.accept(friend)
        messages.add_message(request, messages.SUCCESS, _('Friend offer accepted'))

    return redirect('friends:list')

@login_required
def offers_inbox(request):
    return direct_to_template(request, 'friends/inbox.html')

@login_required
def offers_sent(request):
    return direct_to_template(request, 'friends/sent.html')