# -*- coding: utf-8 -*-

import sys
import re

import datetime
from apps.billing.documents import Tariff
from apps.cam.documents import Camera, CameraType, CameraTag
from apps.cam.forms import CameraForm
from apps.invite.documents import Invite

from apps.media.forms import PhotoForm

from django.views.generic.simple import direct_to_template

from django.contrib.auth import (SESSION_KEY,
    BACKEND_SESSION_KEY,
    logout as django_logout)

from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, HttpResponseNotFound
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.template import Context, loader

from django.views.debug import ExceptionReporter
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.contrib.auth import REDIRECT_FIELD_NAME

from mongoengine.django.shortcuts import get_document_or_404

from apps.user_messages.forms import MessageTextForm
from apps.social.forms import ChangeProfileForm, LostPasswordForm
from apps.social.forms import SetNewPasswordForm
from apps.utils.paginator import paginate

from forms import UserCreationForm, LoginForm
from documents import User
from forms import PeopleFilterForm
from apps.social.documents import Profile


def filter(request):

    return direct_to_template(request, 'index.html', {
        'form': form,
        'accounts': users,
    })



def index(request):
    if not request.user.is_authenticated():
        return _index_unreg(request)

    params = dict(request.GET.items())
    if 'page' in params:
        del params['page']

    form = PeopleFilterForm(params or None)

    if params and form.is_valid():
        filter_user_data = {}
        filter_profile_data = {}

        data = dict(form.cleaned_data)

        filter_user_data['is_active'] = True

        if data['first_name']:
            filter_user_data['first_name__icontains'] = data['first_name']

        if data['last_name']:
            filter_user_data['last_name__icontains'] = data['last_name']

        if data['gender']:
            filter_profile_data['sex'] = data['gender']

        if data['has_photo']:
            filter_user_data['avatar__exists'] = True

        if data['is_online']:
            filter_user_data.update(
            {'last_access__gt': User.get_delta_time()
            })

        if filter_profile_data:
            profiles = Profile.objects.filter(**filter_profile_data).only('user')
            if filter_user_data:
                user_ids = [profile.user.id for profile in profiles]
                filter_user_data['id__in'] = user_ids
                users = User.objects.filter(**filter_user_data)
            else:
                users = [profile.user for profile in profiles]

        else:
            users = User.objects.filter(**filter_user_data)

        users_count = len(users)
    
    else:
        users = User.objects(last_access__gt=User.get_delta_time(), is_active=True)
        users_count = User.objects(last_access__gt=User.get_delta_time(), is_active=True).count()

    objects = paginate(request,
                       users,
                       users_count,
                       28)

    if request.is_ajax():
        return direct_to_template(request, '_user_list.html', {
            'objects': objects,
        })
    else:
        return direct_to_template(request, 'index.html', {
            'objects': objects,
            'form': form
        })


def _index_unreg(request):
    from apps.news.documents import News
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
    return direct_to_template(request, 'index_unreg.html', {
        'base_template': "base_info.html",
        'reg_form': reg_form,
        'login_form': login_form,
        'is_reg': is_reg,
        'news_list': News.objects,
        })


def static(request, page):
    return direct_to_template(request, 'static/%s.html' % page, {
        'base_template': "base.html" if request.user.is_authenticated() else "base_info.html" })


def register(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        user = User(
                    first_name=form.cleaned_data['first_name'],
                    last_name=form.cleaned_data['last_name'],
                    email=form.cleaned_data['email'],
                    phone=form.cleaned_data['phone'],
                    is_active=False
                    )
        user.gen_activation_code()
        user.set_password(form.cleaned_data['password1'])
        user.save()
        user.send_activation_code()

        invite_id = request.session.get('invite_id')

        if invite_id:
            invite = Invite.objects.with_id(invite_id)

            # временная заглушка для неуникальных приглашений
            inviter = User.objects.with_id(invite_id)
            if not invite and inviter:
                invite = Invite(sender=inviter)
                invite.save()
            # временная заглушка для неуникальных приглашений end

            if invite:
                if invite.recipient:
                    messages.add_message(request, messages.WARNING,
                             _('The invitation has already been used by another user'))
                else:
                    invite.register(user)
            else:
                messages.add_message(request, messages.WARNING,
                             _('Incorrect reference to an invitation'))

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

    invite = Invite.objects(recipient=user).first()
    if invite:
        invite.on_activate()

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

    invitee_count = Invite.invitee_count(request.user)

    return direct_to_template(request, 'social/home.html', {
        'invitee_count': invitee_count,
        'camera': camera,
        'is_owner': True,
        'profile': profile,
        'settings': settings
    })


def home_conference(request):
    return direct_to_template(request, 'social/user_conference.html')


def user_conference(request, user_id):
    return direct_to_template(request, 'social/user_conference.html', { 'callid': user_id })


def user(request, user_id=None):
    page_user = get_document_or_404(User, id=user_id)
    if page_user == request.user:
        return redirect('social:home')

    profile = page_user.profile
    profile.sex = dict(ChangeProfileForm.SEX_CHOICES).get(profile.sex, ChangeProfileForm.SEX_CHOICES[0][1])
    msgform = MessageTextForm()
    invitee_count = Invite.invitee_count(page_user)
    is_friend = not request.user.friends.can_add(page_user)

    data = {
        'page_user': page_user,
        'profile': profile,
        'invitee_count': invitee_count,
        'msgform': msgform,
        'show_friend_button': not is_friend,
        'settings': settings
    }

    camera = page_user.get_camera()
    if camera:
        data.update({
            'camera': camera,
            'show_bookmark_button': camera.can_bookmark_add(request.user),
            'show_view_access_link': camera.is_view_enabled and
                                     camera.is_view_paid and
                                     camera.is_view_public or
                                     is_friend,
            'show_manage_access_link': camera.is_management_enabled and
                                       camera.is_managed and
                                       camera.is_management_paid and
                                       camera.is_management_public or
                                       is_friend,
        })
        camera.show = camera.can_show(page_user, request.user)
        camera.manage = camera.can_manage(page_user, request.user)
    return direct_to_template(request, 'social/user.html', data)


def avatar_edit(request):
    user = request.user
    if request.method != 'POST':
        form = PhotoForm()
    else:
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            user.avatar = form.fields['file'].save('avatar',
                                                     settings.AVATAR_SIZES, 'AVATAR_RESIZE')
            user.save()

            messages.add_message(request, messages.SUCCESS, _('Avatar successfully updated'))
            return HttpResponseRedirect(request.path)


    return direct_to_template(request, 'social/profile/avatar.html',
                              dict(form=form, user=user)
                              )


def profile_edit(request, id=None):
    def _profile_edit():
        if id:
            user = get_document_or_404(User, id=id)
            if not request.user.is_superuser and user.id != request.user.id:
                return HttpResponseNotFound()
        else:
            user = request.user
        context = profile_form(request, user)
        if not context:
            return

        camera = user.get_camera()
        if camera or request.user.is_superuser:
            answer = cam_form(request, user, camera)
            if not answer:
                return
            context.update(answer)
            if answer['camera']:
                answer = screen_form(request, answer['camera'])
                if not answer:
                    return
                context.update(answer)
        return context

    context = _profile_edit()
    if not context:
        if id:
            return redirect(reverse('social:user', args=[id]))
        else:
            return redirect('social:home')
    return direct_to_template(request, 'social/profile/edit.html', context)


def profile_form(request, user):
    profile = user.profile
    if request.POST and request.POST.get('form', None) == 'profile':
        form = ChangeProfileForm(request.POST)
        if form.is_valid():
            for k, v in form.cleaned_data.items():
                setattr(profile, k, v if v else None)
            profile.save()
            messages.add_message(request, messages.SUCCESS, _('Profile successfully updated'))
            return
    else:
        form = ChangeProfileForm(profile._data)
    return dict(profile_form=form, user=user)


def cam_form(request, user, cam):
    if cam:
        initial = cam._data
        initial['type'] = cam.type.get_option_value()
        initial['operator'] = initial['operator'] and initial['operator'].id
        initial['tags'] = initial['tags'] and [i.id for i in initial['tags']]
        for tariff_type in Camera.TARIFF_FIELDS:
            value = getattr(cam, tariff_type)
            if value:
                initial[tariff_type] = value.id
    else:
        initial = {}

    if request.POST and request.POST.get('form', None) == 'cam':
        form = CameraForm(user, request.POST, initial=initial)
        if form.is_valid():
            if not cam:
                cam = Camera()
                cam.owner = user
                old_tag_ids = []
            elif form.cleaned_data['tags']:
                old_tag_ids = map(str, cam.tags)


            for k, v in form.cleaned_data.items():
                setattr(cam, k, v)

            cam.type = CameraType.objects.get(id=form.cleaned_data['type'][:-2])
            cam.operator = form.cleaned_data['operator'] and User.objects(id=form.cleaned_data['operator']).first() or None
            if form.cleaned_data['tags']:
                new_tag_ids = map(str, form.cleaned_data['tags'])
                CameraTag.calc_count(new_tag_ids, old_tag_ids)
                cam.tags = CameraTag.objects(id__in=form.cleaned_data['tags'])


            for tariff_type in Camera.TARIFF_FIELDS:
                value = form.cleaned_data[tariff_type]
                if value:
                    value = Tariff.objects.get(id=value)
                    assert value in getattr(Tariff, 'get_%s_list' % tariff_type)()
                    setattr(cam, tariff_type, value)
                else:
                    setattr(cam, tariff_type, None)

            cam.save()
            messages.add_message(request, messages.SUCCESS, _('Camera successfully updated'))
            return
    else:
        form = CameraForm(user, None, initial=initial)

    return dict(cam_form=form, camera=cam)


def screen_form(request, camera):
    if request.POST and request.POST.get('form', None) == 'screen':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            camera.screen = form.fields['file'].save('camera_screen', settings.SCREEN_SIZES, 'CAM_SCREEN_RESIZE')
            camera.save()
            messages.add_message(request, messages.SUCCESS, _('Screen successfully updated'))
            return
    else:
        form = PhotoForm()

    return dict(screen_form=form, screen=camera.screen)


def in_dev(request):
    return direct_to_template(request, 'in_dev.html' , {
        'base_template': "base.html" if request.user.is_authenticated() else "base_info.html" })


def test_error(request):
    raise Exception()


def test_messages(request):
    messages.add_message(request, messages.SUCCESS, 'Успех')
    messages.add_message(request, messages.ERROR, 'Ошибка')
    messages.add_message(request, messages.WARNING, 'Предупреждение')

    return redirect('social:index')


def server_error(request):
    exc_info = sys.exc_info()
    reporter = ExceptionReporter(request, *exc_info)
    html = reporter.get_traceback_html()
    msg = EmailMessage('server_error@%s' % request.path,
                       html, settings.ROBOT_EMAIL_ADDRESS,
                       [ '%s <%s>' % (name, address)
                         for name, address in settings.ADMINS])

    msg.content_subtype = "html"

    msg.send(fail_silently=True)

    template_name = '500.html'
    t = loader.get_template(template_name)
    #logging.getLogger('server_error').error(request)
    return HttpResponseServerError(t.render(Context({})))


def lost_password(request, template='social/lost_password.html'):
    if request.method == 'POST':
        form = LostPasswordForm(request.POST)
        if form.is_valid():
            user = User.objects(email=form.cleaned_data['email']).first()
            if user:
                if user.is_active:
                    user.gen_activation_code()
                    user.save()
                    user.send_restore_password_code()
                else:
                    user.send_activation_code()
            messages.add_message(request, messages.SUCCESS, _('Email with a link sent to restore the address you specify.'))
            return redirect('social:index')
    else:
        form = LostPasswordForm()
    return direct_to_template(request, template , dict(form=form))


def recovery_password(request, code):
    try:
        user = User.objects.get(is_active=True, activation_code=code)
    except:
        messages.add_message(request, messages.ERROR,
                             _('Recovery code corrupted or already used'))
        return redirect('social:index')

    # django needs a backend annotation
    from django.contrib.auth import get_backends
    backend = get_backends()[0]
    user.backend = "%s.%s" % (backend.__module__, backend.__class__.__name__)
    django_login(request, user)
    return redirect(reverse('social:set_new_password', args=[code]))


def set_new_password(request, code):
    if request.user.activation_code != code:
        return HttpResponseNotFound()
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['password1'])
            request.user.activation_code = None
            request.user.save()
            messages.add_message(request, messages.SUCCESS, _('Password successfully updated.'))
            return redirect('social:home')
    else:
        form = SetNewPasswordForm()
    return direct_to_template(request, 'social/profile/set_new_password.html' , dict(form=form))

