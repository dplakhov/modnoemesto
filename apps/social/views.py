
from django.views.generic.simple import direct_to_template
from django.contrib.auth import (authenticate, login as django_login,
    logout as django_logout)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from mongoengine.django.shortcuts import get_document_or_404

from documents import (Account, FriendshipOffer, Message,
        LimitsViolationException)
from forms import UserCreationForm, LoginForm, MessageTextForm


def index(request):
    accs = Account.objects()
    return direct_to_template(request, 'index.html', { 'accs': accs })


def register(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        user = Account.create_user(form.data['username'],
                                   form.data['password1'])
        user = authenticate(username=user.username, password=form.data['password1'])
        django_login(request, user)
        return redirect('social:home')

    return direct_to_template(request, 'registration.html', { 'form': form })


def login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username, password = form.data['username'], form.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                return redirect('social:home')
            else:
                return direct_to_template(request, 'disabled_account.html')
    return direct_to_template(request, 'login.html', { 'form': form })


def logout(request):
    django_logout(request)
    return redirect('/')


@login_required
def home(request):
    return direct_to_template(request, 'social/home.html')


def user(request, user_id=None):
    page_user = get_document_or_404(Account, id=user_id)
    if page_user == request.user:
        return redirect('social:home')

    show_friend_button = request.user.is_authenticated() and not (page_user in
            request.user.mutual_friends or
            FriendshipOffer.objects(author=request.user,
                               recipient=page_user).count())

    msgform = MessageTextForm()
    return direct_to_template(request, 'social/user.html',
                              { 'page_user': page_user, 'msgform': msgform,
                                'show_friend_button': show_friend_button })


@login_required
def friend(request, user_id):
    if request.user.id == user_id:
        return redirect('social:home')
    some_user = get_document_or_404(Account, id=user_id)
    try:
        request.user.friend(some_user)
    except LimitsViolationException:
        pass #@todo: display some message, describing the situation

    return redirect('social:home')


@login_required
def unfriend(request, user_id):
    if request.user.id == user_id:
        return redirect('social:home')
    some_user = get_document_or_404(Account, id=user_id)
    request.user.unfriend(some_user)
    return redirect('social:home')


@login_required
def view_fs_offers_inbox(request):
    #@todo: pagination
    offers = FriendshipOffer.objects(recipient=request.user)\
        .order_by('-timestamp')[:10]
    return direct_to_template(request, 'social/friendship/inbox.html',
                              { 'offers': offers })


@login_required
def view_fs_offers_sent(request):
    #@todo: pagination
    offers = FriendshipOffer.objects(author=request.user)\
        .order_by('-timestamp')[:10]
    return direct_to_template(request, 'social/friendship/sent.html',
                              { 'offers': offers })


@login_required
def cancel_fs_offer(request, offer_id):
    offer = get_document_or_404(FriendshipOffer, id=offer_id)
    if offer.author.id != request.user.id:
        raise Http404()
    offer.delete()
    return redirect('social:view_fs_offers_sent')


@login_required
def decline_fs_offer(request, offer_id):
    offer = get_document_or_404(FriendshipOffer, id=offer_id)
    if offer.recipient.id != request.user.id:
        raise Http404()
    offer.delete()
    return redirect('social:view_fs_offers_inbox')

@login_required
def send_message(request, user_id):
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
    return direct_to_template(request, 'social/messages/inbox.html',
                              { 'msgs': messages })


@login_required
def view_sent(request):
    #@todo: pagination
    #@todo: partial data fetching
    messages = reversed(request.user.msg_sent[-10:])
    return direct_to_template(request, 'social/messages/sent.html',
                              { 'msgs': messages })


@login_required
def view_message(request, message_id):
    message = get_document_or_404(Message, id=message_id, userlist=request.user)
    if message.recipient == request.user and not message.is_read:
        Account.objects(id=request.user.id).update_one(dec__unread_msg_count=1)
        Message.objects(id=message.id).update_one(set__is_read=True)
    return direct_to_template(request, 'social/messages/message.html',
                              { 'msg': message })


@login_required
def delete_message(request, message_id):
    message = get_document_or_404(Message, id=message_id, userlist=request.user)
    message.delete_from(request.user)
    return redirect('social:view_inbox')
