# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template

from mongoengine.django.shortcuts import get_document_or_404

from .forms import GroupCreationForm
from .documents import Group

#@login_required
from apps.groups.documents import GroupTheme, GroupType
from apps.groups.forms import ThemeForm, TypeForm
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
    return direct_to_template(request, 'groups/user_group_list.html',
                              dict(groups=groups)
                              )


#@login_required
def group_edit(request, id=None):
    if id:
        group = get_document_or_404(Group, id=id)
        is_admin = group.is_admin(request.user) or request.user.is_superuser
        if not is_admin:
            return redirect(reverse('groups:group_view', kwargs=dict(id=group.pk)))
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
        return redirect(reverse('groups:group_view', kwargs=dict(id=group.pk)))
    return direct_to_template(request, 'groups/group_edit.html', dict(form=form))


#@login_required
def group_view(request, id):
    group = get_document_or_404(Group, id=id)
    return direct_to_template(request, 'groups/view.html', {
        'group': group,
        'is_admin': group.is_admin(request.user) or request.user.is_superuser,
    })

#@login_required
def group_join(request, id):
    group = get_document_or_404(Group, id=id)
    group.add_member(request.user)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))


#@login_required
def group_leave(request, id):
    group = get_document_or_404(Group, id=id)
    group.remove_member(request.user)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))


#@login_required
def group_join_user(request, id, user_id):
    group = get_document_or_404(Group, id=id)
    if not group.is_admin(request.user):
        return redirect(reverse('groups:group_view', kwargs=dict(id=id)))
    user = get_document_or_404(User, id=user_id)
    group.add_member(user, is_invite = True)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))


#@login_required
def group_leave_user(request, id, user_id):
    group = get_document_or_404(Group, id=id)
    if not group.is_admin(request.user):
        return redirect(reverse('groups:group_view', kwargs=dict(id=id)))
    user = get_document_or_404(User, id=user_id)
    group.remove_member(user)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))


@permission_required('superuser')
def theme_list(request):
    themes = GroupTheme.objects.all()
    return direct_to_template(request, 'groups/theme_list.html',
                              dict(themes=themes)
                              )


@permission_required('superuser')
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


@permission_required('superuser')
def theme_delete(request, id):
    get_document_or_404(GroupTheme, id=id).delete()
    return redirect('groups:theme_list')


@permission_required('superuser')
def type_list(request):
    types = GroupType.objects.all()
    return direct_to_template(request, 'groups/type_list.html',
                              dict(types=types)
                              )


@permission_required('superuser')
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


@permission_required('superuser')
def type_delete(request, id):
    get_document_or_404(GroupType, id=id).delete()
    return redirect('groups:type_list')