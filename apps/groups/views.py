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

def group_list(request):
    #@todo: pagination
    #@todo: partial data fetching
    groups = Group.objects[:10]
    return direct_to_template(request, 'groups/list.html',
                              dict(groups=groups)
                              )


#@login_required
def group_edit(request, id=None):
    if id:
        group = get_document_or_404(Group, id=id)
        initial = group._data
    else:
        group = None
        initial = {}

    form = GroupCreationForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not group:
            group = Group()
            #@todo: need join user as admin

        for k, v in form.cleaned_data.items():
            if v or getattr(group, k):
                setattr(group, k, v)

        group.save()
        return redirect(reverse('groups:group_view', kwargs=dict(id=group.pk)))
    return direct_to_template(request, 'groups/create.html', dict(form=form))


#@login_required
def group_view(request, id):
    group = get_document_or_404(Group, id=id)
    return direct_to_template(request, 'groups/view.html', {
        'group': group,
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