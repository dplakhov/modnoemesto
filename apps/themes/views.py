# -*- coding: utf-8 -*-
from django.http import HttpResponse, Http404

from mongoengine.django.shortcuts import get_document_or_404

from .documents import Theme

def file_view(request, theme_id, file_name):
    theme = get_document_or_404(Theme, id=theme_id)

    file = theme.files[file_name]
    if not file:
        raise Http404()

    response = HttpResponse(file.file.read(),
                        content_type=file.file.content_type)

    response['Last-Modified'] = file.file.upload_date
    return response
