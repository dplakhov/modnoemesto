# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404
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
    form = ThemeAddForm(request.POST or None, request.FILES)
    return direct_to_template(request,
                              'themes/list.html',
                              dict(form=form)
                              )
def list(request):
    pass

def delete(request):
    pass
