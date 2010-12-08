# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.template.loader import render_to_string

from django.contrib.auth import (SESSION_KEY,
    BACKEND_SESSION_KEY,
    logout as django_logout)

import datetime

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from mongoengine.django.shortcuts import get_document_or_404

from documents import (User, LimitsViolationException)
from forms import ( UserCreationForm, LoginForm, ChangeAvatarForm)

from apps.user_messages.forms import MessageTextForm 

from apps.media.documents import File
from apps.media.transformations.image import ImageResize
from apps.groups.documents import Group

from ImageFile import Parser as ImageFileParser


from apps.billing.documents import AccessCamOrder
from apps.social.forms import ChangeProfileForm
import re
from apps.social.documents import Profile, Setting


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from apps.media.tasks import apply_file_transformations
from django.contrib.auth import REDIRECT_FIELD_NAME


def index(request):
    if not request.user.is_authenticated():
        return about(request)
    accs = User.objects(last_access__gt=User.get_delta_time()).only('username', 'avatar')
    return direct_to_template(request, 'index.html', { 'accs': accs })


def about(request):
    if request.user.is_authenticated():
        return direct_to_template(request, 'about.html', {
            'base_template': "base.html",
            'is_auth': True })
    reg_form = None
    login_form = None
    if request.method == "POST":
        form_name = request.POST.get('form_name', None)
        if form_name == 'register':
            reg_form = register(request)
            if type(reg_form) == HttpResponse:
                return reg_form
        elif form_name == 'login':
            login_form = login(request)
            if type(login_form) == HttpResponseRedirect:
                return login_form
    is_reg = reg_form is not None
    reg_form = reg_form or UserCreationForm()
    login_form = login_form or LoginForm()
    request.session.set_test_cookie()
    return direct_to_template(request, 'about.html', {
        'base_template': "base_info.html",
        'reg_form': reg_form,
        'login_form': login_form,
        'is_reg': is_reg,
        })

def register(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        from random import choice
        alpha = 'abcdef0123456789'
        activation_code = ''.join(choice(alpha) for _ in xrange(12))
        user = User(username=form.data['username'],
                    full_name=form.data['full_name'],
                    phone=form.data['phone'],
                    is_active=False,
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

    return form

def django_login(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    user.last_login = datetime.datetime.now()
    user.save()

    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != str(user.id):
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = str(user.id)
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user



def activation(request, code=None):
    try:
        user = User.objects.get(is_active=False, activation_code=code)
    except:
        messages.add_message(request, messages.ERROR,
                             _('Activation code corrupted or already used'))
        return redirect('social:index')
        
    user.is_active = True
    # django needs a backend annotation
    from django.contrib.auth import get_backends
    backend = get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    django_login(request, user)
    return redirect('social:home')


def login(request):
    form = LoginForm(request, data=request.POST)
    if form.is_valid():
        redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, 'social:home')
        if not redirect_to or ' ' in redirect_to:
            redirect_to = settings.LOGIN_REDIRECT_URL

        elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
                redirect_to = settings.LOGIN_REDIRECT_URL

        django_login(request, form.get_user())

        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()

        return redirect(redirect_to)
    return form


def logout(request):
    django_logout(request)
    return redirect('/')


def home(request):
    camera = request.user.get_camera()
    if camera:
        camera.show = True
    #@todo: need filter
    profile = request.user.profile
    profile.sex = dict(ChangeProfileForm.SEX_CHOICES).get(profile.sex, ChangeProfileForm.SEX_CHOICES[0][1])
    return direct_to_template(request, 'social/home.html', {
        'camera': camera,
        'is_owner': True,
        'profile': profile,
    })


def user(request, user_id=None):
    page_user = get_document_or_404(User, id=user_id)
    if page_user == request.user:
        return redirect('social:home')

    page_user.is_friend = request.user.is_authenticated() and \
                          request.user.friends.contains(page_user)

    show_friend_button = request.user.is_authenticated() and \
                         request.user.friends.can_add(page_user)

    camera = page_user.get_camera()
    if camera:
        camera.show = camera.can_show(page_user)
    msgform = MessageTextForm()
    return direct_to_template(request, 'social/user.html',
                              { 'page_user': page_user, 'msgform': msgform,
                                'show_friend_button': show_friend_button,
                                'show_bookmark_button': camera and camera.can_bookmark_add(request.user),
                                'camera': camera })


def avatar(request, user_id, format):
    user = get_document_or_404(User, id=user_id)
    if not user.avatar:
        return redirect('/media/img/notfound/avatar_%s.png' % format)

    try:
        image = user.avatar.get_derivative(format)
    except File.DerivativeNotFound:
        return redirect('/media/img/converting/avatar_%s.png' % format)

    response = HttpResponse(image.file.read(), content_type=image.file.content_type)
    response['Last-Modified'] = image.file.upload_date
    return response


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


def profile_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ChangeProfileForm(request.POST)
        if form.is_valid():
            for k, v in form.cleaned_data.items():
                setattr(profile, k, v if v else None)
            profile.save()
            messages.add_message(request, messages.SUCCESS, _('Profile successfully updated'))
            return redirect('social:home')
    else:
        form = ChangeProfileForm(profile._data)
    return direct_to_template(request, 'social/profile/edit.html',
                              dict(form=form, user=request.user)
                              )


def agreement(request):
    return direct_to_template(request, 'agreement.html' , {
        'base_template': "base.html" if request.user.is_authenticated() else "base_info.html" })


def in_dev(request):
    return direct_to_template(request, 'in_dev.html' , {
        'base_template': "base.html" if request.user.is_authenticated() else "base_info.html" })