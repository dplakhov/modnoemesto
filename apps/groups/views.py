# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect
from django.utils.importlib import import_module
from django.views.generic.simple import direct_to_template
from django.contrib import messages
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib.auth import SESSION_KEY

from mongoengine.django.shortcuts import get_document_or_404

from apps.utils.paginator import paginate
from apps.social.documents import User
from apps.media.forms import PhotoForm


from .forms import GroupCreationForm, MessageTextForm
from .forms import ThemeForm, TypeForm

from .documents import Group
from .documents import GroupTheme, GroupType, GroupUser, GroupMessage

from .decorators import check_admin_right


def group_list(request):
    objects = paginate(request,
                       Group.objects,
                       Group.objects.count(),
                       24)
    return direct_to_template(request, 'groups/list.html', dict(objects=objects))


def user_group_list(request):
    groups = request.user.groups
    groups_invites = request.user.groups_invites
    groups_requests = request.user.groups_requests
    return direct_to_template(request, 'groups/user_group_list.html',
                              dict(groups=groups,
                                   groups_invites=groups_invites,
                                   groups_requests=groups_requests)
                              )


def group_view(request, id):
    group = get_document_or_404(Group, id=id)
    is_active = group.is_active(request.user)

    is_ajax = request.is_ajax()

    if request.POST:
        if not is_active:
            if is_ajax:
                return HttpResponse('')
            else:
                messages.add_message(request, messages.ERROR,
                                 _('To send a message, you need to join the group.'))
                return redirect(reverse('groups:group_view', args=[id]))
        form = MessageTextForm(request.POST)
        if form.is_valid():
            message = GroupMessage(
                group=group,
                sender=request.user,
                text=form.cleaned_data['text'],
            )
            message.save()
            if not is_ajax:
                return redirect(reverse('groups:group_view', args=[id]))
        elif is_ajax:
            return HttpResponse('')
    elif not is_ajax:
        form = MessageTextForm()

    objects = paginate(request,
                       GroupMessage.objects(group=group),
                       GroupMessage.objects(group=group).count(),
                       settings.MESSAGES_ON_PAGE)

    if is_ajax:
        return direct_to_template(request, 'groups/_comments.html', dict(
            group=group,
            is_admin=group.is_admin(request.user) or request.user.is_superuser,
            objects=objects,
        ))
    else:
        admins = []
        members = []
        for info in GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE):
            if info.is_admin:
                admins.append(info.user)
            else:
                members.append(info.user)
        return direct_to_template(request, 'groups/view.html', dict(
            group=group,
            admins=admins,
            members=members,
            is_admin=group.is_admin(request.user) or request.user.is_superuser,
            can_view_private=group.public or is_active or request.user.is_superuser,
            can_view_conference=is_active or request.user.is_superuser,
            can_send_message=is_active,
            is_status_request=group.is_request(request.user),
            objects=objects,
            form=form,
            members_count=GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE).count(),
        ))


def group_conference(request, id):
    group = get_document_or_404(Group, id=id)
    is_active = group.is_active(request.user)
    if not (is_active or request.user.is_superuser):
        return redirect(reverse('groups:group_view', args=[id]))
    return direct_to_template(request, 'groups/group_conference.html', dict(
        group=group,
        is_admin=group.is_admin(request.user) or request.user.is_superuser,
    ))


def api_member_list(request, id, format):
    group = get_document_or_404(Group, id=id)
    mimetypes = dict(
            txt='text/plain',
            xml='xml/plain',
                     )

    return direct_to_template(request,
                              'groups/member_list.%s' % format,
                              dict(list=GroupUser.objects(group=group,
                                                          status=GroupUser.STATUS.ACTIVE)),
                              mimetype=mimetypes[format]
                              )


def member_list(request, id):
    group = get_document_or_404(Group, id=id)
    can_view = group.public or group.is_active(request.user) or request.user.is_superuser
    if not can_view:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[id]))

    objects = paginate(request,
                       GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE),
                       GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE).count(),
                       settings.GROUP_USERS_ON_PAGE)
    return direct_to_template(request,
                              'groups/member_list.html',
                              dict(group=group,
                                   objects=objects),
                              )


def can_manage(request):
    def calc():
        session_key = request.GET.get('session_key')
        group_id = request.GET.get('group_id')
        if not (session_key and group_id):
            return 'BAD_PARAMS'
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            return 'BAD_SESSION KEY'
        user = User.objects.with_id(user_id)
        if not user:
            return 'BAD_USER'

        group = Group.objects.with_id(group_id)
        if not group:
            return 'BAD_GROUP'

        group_user = GroupUser.objects(user=user, group=group).first()

        if user.is_superuser or (group_user and group_user.is_admin):
            return 'OK'

        return 'ACCESS_DENIED'

    return HttpResponse('&result=%s' % calc(), mimetype='text/plain')


@check_admin_right
def members_manage(request, group):
    admins = []
    members = []
    for info in GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE):
        if info.is_admin:
            admins.append(info.user)
        else:
            members.append(info.user)
    return direct_to_template(request, 'groups/members_manage.html', {
        'group': group,
        'admins': admins,
        'members': members,
    })


@check_admin_right
def give_admin_right(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    group.give_admin_right(user)
    return redirect(reverse('groups:members_manage', args=[group.id]))


@check_admin_right
def remove_admin_right(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    if group.can_remove_member(user):
        group.remove_admin_right(user)
    else:
        messages.add_message(request, messages.ERROR,
                             _('You can not leave the group. Give the administrator rights to another party.'))
    return redirect(reverse('groups:members_manage', args=[group.id]))


@check_admin_right
def remove_member(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    if group.can_remove_member(user):
        group.remove_member(user)
    else:
        messages.add_message(request, messages.ERROR,
                             _('You can not leave the group. Give the administrator rights to another party.'))
    return redirect(reverse('groups:members_manage', args=[group.id]))


def group_edit(request, id=None):
    if id:
        group = get_document_or_404(Group, id=id)
        is_admin = group.is_admin(request.user) or request.user.is_superuser
        if not is_admin:
            messages.add_message(request, messages.ERROR, _('You are not allowed.'))
            return redirect(reverse('groups:group_view', args=[id]))
        initial = group._data
    else:
        initial = Group()._data

    form = GroupCreationForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not id:
            group = Group()

        for k, v in form.cleaned_data.items():
            if v or getattr(group, k):
                setattr(group, k, v)

        group.save()
        if not id:
            group.add_member(request.user, is_admin=True)
        return redirect(reverse('groups:group_view', args=[group.id]))
    return direct_to_template(request, 'groups/group_edit.html', dict(form=form,
                                                                      is_new=id is None,
                                                                      is_public=group.public if id else True,
                                                                      group=id and group))


@check_admin_right
def photo_edit(request, group):
    if request.method != 'POST':
        form = PhotoForm()
    else:
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            group.photo = form.fields['file'].save('group_photo', settings.GROUP_PHOTO_SIZES, 'GROUP_PHOTO_RESIZE')
            group.save()
            messages.add_message(request, messages.SUCCESS, _('Photo successfully updated'))
            return HttpResponseRedirect(request.path)
    return direct_to_template(request, 'groups/photo_edit.html',
                              dict(form=form, photo=group.photo, group=group)
                              )


@check_admin_right
def send_friends_invite(request, group):
    friends = []
    members = dict((i.user.id, i.status) for i in GroupUser.objects(group=group))
    for user in request.user.friends.list:
        if user.id not in members.keys():
            friends.append((user, True))
        elif members.get(user.id, None) == GroupUser.STATUS.INVITE:
            friends.append((user, False))
    return direct_to_template(request, 'groups/send_friends_invite.html', dict(
        group=group,
        friends=friends))


@check_admin_right
def send_invite(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    group.add_member(user, status=GroupUser.STATUS.INVITE)
    if request.is_ajax():
        return HttpResponse('OK')
    else:
        return redirect(reverse('groups:send_friends_invite', args=[group.id]))


@check_admin_right
def cancel_invite(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    GroupUser.objects(group=group, user=user, status=GroupUser.STATUS.INVITE).delete()
    return redirect(reverse('groups:send_friends_invite', args=[group.id]))


def invite_take(request, id):
    GroupUser.objects(group=id, user=request.user.id, status=GroupUser.STATUS.INVITE)\
             .update_one(set__status=GroupUser.STATUS.ACTIVE)
    return redirect(reverse('groups:group_view', args=[id]))


def cancel_request(request, id):
    group = get_document_or_404(Group, id=id)
    GroupUser.objects(group=group, user=request.user, status=GroupUser.STATUS.REQUEST).delete()
    return redirect(reverse('groups:group_view', args=[group.id]))


def invite_refuse(request, id):
    GroupUser.objects(group=id, user=request.user.id, status=GroupUser.STATUS.INVITE).delete()
    return redirect('groups:user_group_list')


def request_take(request, id):
    info = get_document_or_404(GroupUser, id=id)
    if not info.group.is_admin(request.user):
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
    else:
        if info.status == GroupUser.STATUS.REQUEST:
            info.status = GroupUser.STATUS.ACTIVE
            info.save()
    return redirect(reverse('groups:user_group_list'))


def request_refuse(request, id):
    info = get_document_or_404(GroupUser, id=id)
    if not info.group.is_admin(request.user):
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
    else:
        if info.status == GroupUser.STATUS.REQUEST:
            info.delete()
    return redirect(reverse('groups:user_group_list'))


def group_join(request, id):
    group = get_document_or_404(Group, id=id)
    status = GroupUser.STATUS.ACTIVE if group.public else GroupUser.STATUS.REQUEST
    group.add_member(request.user, status=status)
    return redirect(reverse('groups:group_view', args=[id]))


def group_leave(request, id):
    group = get_document_or_404(Group, id=id)
    if group.can_remove_member(request.user):
        group.remove_member(request.user)
    else:
        messages.add_message(request, messages.ERROR,
                             _('You can not leave the group. Give the administrator rights to another party.'))
    return redirect(reverse('groups:group_view', args=[id]))


@check_admin_right
def group_join_user(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    group.add_member(user, status=GroupUser.STATUS.ACTIVE)
    return redirect(reverse('groups:group_view', args=[id]))


@check_admin_right
def group_leave_user(request, group, user_id):
    user = get_document_or_404(User, id=user_id)
    group.remove_member(user)
    return redirect(reverse('groups:group_view', args=[id]))


@check_admin_right
def delete_message(request, group, message_id):
    get_document_or_404(GroupMessage, id=message_id).delete()
    if request.is_ajax():
        objects = paginate(request,
                           GroupMessage.objects(group=group),
                           GroupMessage.objects(group=group).count(),
                           settings.MESSAGES_ON_PAGE)
        return direct_to_template(request, 'groups/_comments.html', dict(
            group=group,
            is_admin=group.is_admin(request.user) or request.user.is_superuser,
            objects=objects,
        ))
    else:
        return redirect(reverse('groups:group_view', args=[group.id]))


def send_my_invites_to_user(request, user_id):
    user = get_document_or_404(User, id=user_id)
    user_groups = [i.group.id for i in GroupUser.objects(user=user).only('group')]
    groups = []
    for info in GroupUser.objects(user=request.user, is_admin=True).only('group'):
        group = info.group
        if group.id not in user_groups:
            groups.append(group)
    return direct_to_template(request, 'groups/send_my_invites_to_user.html',
                              dict(groups=groups, invite_user=user))


@permission_required('groups')
def theme_list(request):
    themes = GroupTheme.objects.all()
    return direct_to_template(request, 'groups/theme_list.html',
                              dict(themes=themes)
                              )


@permission_required('groups')
def theme_edit(request, id=None):
    if id:
        theme = get_document_or_404(GroupTheme, id=id)
        initial = theme._data
    else:
        theme = None
        initial = {}

    form = ThemeForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not theme:
            theme = GroupTheme()

        for k, v in form.cleaned_data.items():
            setattr(theme, k, v)

        theme.save()
        return redirect('groups:theme_list')

    return direct_to_template(request, 'groups/theme_edit.html',
                              {'form':form, 'is_new':id is None})


@permission_required('groups')
def theme_delete(request, id):
    theme = get_document_or_404(GroupTheme, id=id)
    if Group.objects(theme=theme).count():
        messages.add_message(request, messages.ERROR,
                             _('You can not delete this group theme.'))
    else:
        theme.delete()
        messages.add_message(request, messages.SUCCESS,
                             _('Group theme deleted.'))
            
    return redirect('groups:theme_list')


@permission_required('groups')
def type_list(request):
    types = GroupType.objects.all()
    return direct_to_template(request, 'groups/type_list.html',
                              dict(types=types)
                              )


@permission_required('groups')
def type_edit(request, id=None):
    if id:
        type = get_document_or_404(GroupType, id=id)
        initial = type._data
    else:
        type = None
        initial = {}

    form = TypeForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not type:
            type = GroupType()

        for k, v in form.cleaned_data.items():
            setattr(type, k, v)

        type.save()
        return redirect('groups:type_list')

    return direct_to_template(request, 'groups/type_edit.html',
                              {'form':form, 'is_new':id is None})


@permission_required('groups')
def type_delete(request, id):
    type = get_document_or_404(GroupType, id=id)
    if Group.objects(type=type).count():
        messages.add_message(request, messages.ERROR,
                             _('You can not delete this group type.'))
    else:
        type.delete()
        messages.add_message(request, messages.SUCCESS,
                             _('Group type deleted.'))

    return redirect('groups:type_list')
