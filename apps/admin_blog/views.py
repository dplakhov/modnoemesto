# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required

from mongoengine.django.shortcuts import get_document_or_404

from .documents import AdminBlog
from .forms import AdminBlogForm
from django.core.urlresolvers import reverse

def list(request):
    list = AdminBlog.objects()
    return direct_to_template(request, 'admin_blog/list.html',
                              dict(list=list))


def view(request, id):
    item = get_document_or_404(AdminBlog, id=id)
    return direct_to_template(request, 'admin_blog/view.html',
                              dict(item=item)
                              )


@permission_required('superuser')
def edit(request, id=None):
    if id:
        item = get_document_or_404(AdminBlog, id=id)
        initial = item._data
    else:
        item = None
        initial = {}

    form = AdminBlogForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not item:
            item = AdminBlog()

        for k, v in form.cleaned_data.items():
            if k.startswith('_'):
                continue
            if hasattr(item, k):
                setattr(item, k, v)

        item.author = request.user
        item.save()

        return redirect('admin_blog:list')

    return direct_to_template(request, 'admin_blog/edit.html',
                              dict(
                                    form=form,
                                    is_new=id is None
                                    )
                              )


@permission_required('superuser')
def delete(request, id):
    item = get_document_or_404(AdminBlog, id=id)
    item.delete()
    return redirect('admin_blog:list')

