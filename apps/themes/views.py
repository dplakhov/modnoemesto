# -*- coding: utf-8 -*-
import tempfile
from apps.social.documents import User
from apps.utils.paginator import paginate
from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic.simple import direct_to_template

from mongoengine.django.shortcuts import get_document_or_404

from .documents import Theme
from .forms import ThemeAddForm

def file_view(request, theme_id, file_name):
    theme = get_document_or_404(Theme, id=theme_id)

    file = theme.files[file_name]
    if not file:
        raise Http404()

    response = HttpResponse(file.file.read(),
                        content_type=file.file.content_type)

    response['Last-Modified'] = file.file.upload_date
    return response

def add(request):
    if not request.user.has_perm('themes'):
        raise Http404()

    form = ThemeAddForm(request.POST or None, request.FILES)

    if form.is_valid():
        tmp = tempfile.NamedTemporaryFile()
        for chunk in request.FILES['file'].chunks():
            tmp.write(chunk)

        tmp.flush()
        Theme.from_zip(tmp.name)

    return redirect('themes:list')

def list(request):
    can_manage = request.user.has_perm('themes')
    if can_manage:
        objects = Theme.objects()
    else:
        objects = Theme.objects(is_public=True)

    objects = paginate(request, objects, objects.count(), 25)

    form = ThemeAddForm()

    return direct_to_template(request,
                              'themes/list.html',
                              dict(objects=objects,
                                   form=form,
                                   can_manage=can_manage
                                   )
                              )

def delete(request, theme_id):
    if not request.user.has_perm('themes'):
        raise Http404()

    theme = Theme.objects.with_id(theme_id)

    if theme:
        theme.delete()

    return redirect('themes:list')

def set(request, theme_id, user_id=None):
    has_perm = request.user.has_perm('themes')
    if user_id and not has_perm:
        raise Http404()

    theme = Theme.objects.with_id(theme_id)

    if not theme:
        raise Http404()

    if not theme.is_public and not has_perm:
        raise Http404()

    if user_id:
        user = User.objects.with_id(user_id)
        if not user:
            raise Http404()
    else:
        user = request.user

    profile = user.profile
    profile.theme = theme
    profile.save()

    return redirect('themes:list')

def unset(request, user_id=None):
    if user_id and not request.user.has_perm('themes'):
        raise Http404()

    if user_id:
        user = User.objects.with_id(user_id)
        if not user:
            raise Http404()
    else:
        user = request.user

    profile = user.profile
    profile.theme = None
    profile.save()

    return redirect('themes:list')
