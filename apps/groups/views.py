# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template

from mongoengine.django.shortcuts import get_document_or_404

from .forms import GroupCreationForm
from .documents import Group

@login_required
def group_list(request):
    #@todo: pagination
    #@todo: partial data fetching
    groups = Group.objects[:10]
    return direct_to_template(request, 'groups/list.html',
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
        return redirect(reverse('groups:group_view', kwargs=dict(id=group.pk)))
    return direct_to_template(request, 'groups/create.html', dict(form=form))


@login_required
def group_view(request, id):
    group = get_document_or_404(Group, id=id)
    return direct_to_template(request, 'groups/view.html',
                              dict(group=group))

@login_required
def group_join(request, id):
    group = get_document_or_404(Group, id=id)
    group.add_member(request.user)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))


@login_required
def group_leave(request, id):
    group = get_document_or_404(Group, id=id)
    group.remove_member(request.user)
    return redirect(reverse('groups:group_view', kwargs=dict(id=id)))

