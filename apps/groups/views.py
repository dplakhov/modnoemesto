# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.contrib import messages
from django.utils.translation import ugettext as _

from mongoengine.django.shortcuts import get_document_or_404

from .forms import GroupCreationForm
from .documents import Group

from apps.groups.documents import GroupTheme, GroupType, GroupUser
from apps.groups.forms import ThemeForm, TypeForm, MemberManageForm
from apps.social.documents import User

def group_list(request):
    #@todo: pagination
    #@todo: partial data fetching
    groups = Group.objects[:10]
    return direct_to_template(request, 'groups/list.html',
                              dict(groups=groups)
                              )


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
    admins = []
    members = []
    for info in GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE):
        if info.is_admin:
            admins.append(info.user)
        else:
            members.append(info.user)
    return direct_to_template(request, 'groups/view.html', {
        'group': group,
        'admins': admins,
        'members': members,
        'is_admin': group.is_admin(request.user) or request.user.is_superuser,
        'can_view_private': group.public or group.is_active(request.user) or request.user.is_superuser,
        'is_status_request': group.is_request(request.user),
    })


def members_manage(request, id):
    group = get_document_or_404(Group, id=id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[id]))
    admins = []
    members = []
    for info in GroupUser.objects(group=group, status=GroupUser.STATUS.ACTIVE):
        if info.is_admin:
            admins.append((info.user, info.is_admin))
        else:
            members.append((info.user, info.is_admin))
    return direct_to_template(request, 'groups/members_manage.html', {
        'group': group,
        'admins': admins,
        'members': members,
    })


def give_admin_right(request, group_id, user_id):
    group = get_document_or_404(Group, id=group_id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[group_id]))
    user = get_document_or_404(User, id=user_id)
    group.give_admin_right(user)
    return redirect(reverse('groups:members_manage', args=[group.id]))


def remove_admin_right(request, group_id, user_id):
    group = get_document_or_404(Group, id=group_id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[group_id]))
    user = get_document_or_404(User, id=user_id)
    if group.can_remove_member(user):
        group.remove_admin_right(user)
    else:
        messages.add_message(request, messages.ERROR,
                             _('You can not leave the group. Give the administrator rights to another party.'))
    return redirect(reverse('groups:members_manage', args=[group.id]))


def remove_member(request, group_id, user_id):
    group = get_document_or_404(Group, id=group_id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[group_id]))
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
        initial = {}

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
                                                                      group=group))


def send_friends_invite(request, id):
    group = get_document_or_404(Group, id=id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[id]))
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


def send_invite(request, group_id, user_id):
    group = get_document_or_404(Group, id=group_id)
    user = get_document_or_404(User, id=user_id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[group_id]))
    group.add_member(user, status=GroupUser.STATUS.INVITE)
    return redirect(reverse('groups:send_friends_invite', args=[group_id]))


def cancel_invite(request, group_id, user_id):
    group = get_document_or_404(Group, id=group_id)
    user = get_document_or_404(User, id=user_id)
    is_admin = group.is_admin(request.user) or request.user.is_superuser
    if not is_admin:
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[group_id]))
    GroupUser.objects(group=group, user=user, status=GroupUser.STATUS.INVITE).delete()
    return redirect(reverse('groups:send_friends_invite', args=[group_id]))


def invite_take(request, group_id):
    GroupUser.objects(group=group_id, user=request.user.id, status=GroupUser.STATUS.INVITE)\
             .update_one(set__status=GroupUser.STATUS.ACTIVE)
    return redirect(reverse('groups:group_view', args=[group_id]))


def cancel_request(request, group_id):
    group = get_document_or_404(Group, id=group_id)
    GroupUser.objects(group=group, user=request.user, status=GroupUser.STATUS.REQUEST).delete()
    return redirect(reverse('groups:group_view', args=[group_id]))


def invite_refuse(request, group_id):
    GroupUser.objects(group=group_id, user=request.user.id, status=GroupUser.STATUS.INVITE).delete()
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


def group_join_user(request, id, user_id):
    group = get_document_or_404(Group, id=id)
    if not group.is_admin(request.user):
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[id]))
    user = get_document_or_404(User, id=user_id)
    group.add_member(user, status=GroupUser.STATUS.ACTIVE)
    return redirect(reverse('groups:group_view', args=[id]))


def group_leave_user(request, id, user_id):
    group = get_document_or_404(Group, id=id)
    if not group.is_admin(request.user):
        messages.add_message(request, messages.ERROR, _('You are not allowed.'))
        return redirect(reverse('groups:group_view', args=[id]))
    user = get_document_or_404(User, id=user_id)
    group.remove_member(user)
    return redirect(reverse('groups:group_view', args=[id]))


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
