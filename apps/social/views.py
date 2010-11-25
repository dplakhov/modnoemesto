# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.template.loader import render_to_string
from django.contrib.auth import (authenticate, login as django_login,
    logout as django_logout)
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from mongoengine.django.shortcuts import get_document_or_404

from documents import (Account, FriendshipOffer, Group,
        LimitsViolationException)
from forms import ( UserCreationForm, LoginForm,
    GroupCreationForm, ChangeAvatarForm)

from apps.user_messages.forms import MessageTextForm 

from django.core.urlresolvers import reverse

from apps.media.documents import File
from apps.media.transformations.image import ImageResize

from ImageFile import Parser as ImageFileParser

from django.contrib import messages
from apps.billing.documents import AccessCamOrder

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from apps.media.tasks import apply_file_transformations
from auth import REDIRECT_FIELD_NAME



def index(request):
    accs = Account.objects().only('username', 'avatar')
    return direct_to_template(request, 'index.html', { 'accs': accs })


def register(request):
    form = UserCreationForm(request.POST or None)

    if form.is_valid():
        from random import choice
        alpha = 'abcdef0123456789'
        activation_code = ''.join(choice(alpha) for _ in xrange(12))
        user = Account(username=form.data['username'], is_active=False,
                                   activation_code=activation_code)
        user.set_password(form.data['password1'])
        user.save()

        #@todo: send email in a separate process (queue worker or smth like it)
        #@todo: check email sending results
        email_body = render_to_string('emails/confirm_registration.txt',
                { 'user': user, 'SITE_DOMAIN': settings.SITE_DOMAIN })

        settings.SEND_EMAILS and send_mail('Confirm registration', email_body,
            settings.ROBOT_EMAIL_ADDRESS, [form.data['email']],
            fail_silently=True)

        return direct_to_template(request, 'registration_complete.html')

    return direct_to_template(request, 'registration.html', { 'form': form })


def activation(request, code=None):
    user = get_document_or_404(Account, is_active=False, activation_code=code)
    user.is_active = True
    # django needs a backend annotation
    from django.contrib.auth import get_backends
    backend = get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    django_login(request, user)
    return redirect('social:home')


def login(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username, password = form.data['username'], form.data['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                django_login(request, user)
                redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, 'social:home')
                return redirect(redirect_to)
            else:
                return direct_to_template(request, 'disabled_account.html')
    return direct_to_template(request, 'login.html', { 'form': form })


def logout(request):
    django_logout(request)
    return redirect('/')


@login_required
def home(request):
    camera = request.user.get_camera()
    if camera:
        camera.show = True
    return direct_to_template(request, 'social/home.html', { 'camera': camera, 'is_owner': True })


def user(request, user_id=None):
    page_user = get_document_or_404(Account, id=user_id)
    if page_user == request.user:
        return redirect('social:home')

    page_user.is_friend = request.user.is_authenticated() and (page_user in
                                                 request.user.mutual_friends)

    show_friend_button = request.user.is_authenticated() and not (
            page_user.is_friend or FriendshipOffer.objects(author=request.user,
                recipient=page_user).count())

    camera = page_user.get_camera()
    if camera:
        camera.show = camera.can_show(page_user)
    msgform = MessageTextForm()
    return direct_to_template(request, 'social/user.html',
                              { 'page_user': page_user, 'msgform': msgform,
                                'show_friend_button': show_friend_button,
                                'camera': camera })


@login_required
def user_friends(request):
    return direct_to_template(request, 'social/profile/user_friends.html',
                              { 'frends': request.user })


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
def group_list(request):
    #@todo: pagination
    #@todo: partial data fetching
    groups = Group.objects[:10]
    return direct_to_template(request, 'social/groups/list.html',
                              dict(groups=groups)
                              )


@login_required
def group_add(request):
    form = GroupCreationForm(request.POST or None)
    if form.is_valid():
        name = form.data['name']
        group, created = Group.objects.get_or_create(name=name)
        if created:
            group.add_member(request.user)
        return redirect(reverse('social:group_view', kwargs=dict(id=group.pk)))
    return direct_to_template(request, 'social/groups/create.html', dict(form=form))


@login_required
def group_view(request, id):
    group = get_document_or_404(Group, id=id)
    return direct_to_template(request, 'social/groups/view.html',
                              dict(group=group))

@login_required
def group_join(request, id):
    group = get_document_or_404(Group, id=id)
    group.add_member(request.user)
    return redirect(reverse('social:group_view', kwargs=dict(id=id)))


@login_required
def group_leave(request, id):
    group = get_document_or_404(Group, id=id)
    group.remove_member(request.user)
    return redirect(reverse('social:group_view', kwargs=dict(id=id)))

@login_required
def profile_edit(request):
    return direct_to_template(request, 'social/groups/view.html',
                              )

def avatar(request, user_id, format):
    user = get_document_or_404(Account, id=user_id)
    if not user.avatar:
        return redirect('/media/img/notfound/avatar_%s.png' % format)

    image = user.avatar.get_derivative(format)
    #image = FileDerivative.objects(transformation=format, source=user.avatar).first()

    if not image:
        return redirect('/media/img/converting/avatar_%s.png' % format)

    response = HttpResponse(image.file.read(), content_type=image.file.content_type)
    response['Last-Modified'] = image.file.upload_date
    return response


@login_required
def avatar_edit(request):
    user = request.user
    if request.method != 'POST':
        form = ChangeAvatarForm()
    else:
        form = ChangeAvatarForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            buffer = StringIO()

            for chunk in file.chunks():
                buffer.write(chunk)

            buffer.reset()
            try:
                parser = ImageFileParser()
                parser.feed(buffer.read())
                image = parser.close()
                image_valid = True
            except Exception, e:
                messages.add_message(request, messages.ERROR, _('Invalid image file format'))
                image_valid = False

            if image_valid:
                avatar = File(type='image')
                buffer.reset()
                avatar.file.put(buffer, content_type=file.content_type)
                avatar.save()

                user.avatar = avatar
                user.save()

                transformations = [ ImageResize(name='%sx%s' % (w,h), format='png', width=w, height=h)
                                    for (w, h) in settings.AVATAR_SIZES ]

                if settings.TASKS_ENABLED.get('AVATAR_RESIZE'):
                    args = [ avatar.id, ] + transformations
                    apply_file_transformations.apply_async(args=args)
                else:
                    avatar.apply_transformations(*transformations)

                messages.add_message(request, messages.SUCCESS, _('Avatar successfully updated'))
                return HttpResponseRedirect(request.path)


    return direct_to_template(request, 'social/profile/avatar.html',
                              dict(form=form, user=user)
                              )

