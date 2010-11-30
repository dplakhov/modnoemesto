# -*- coding: utf-8 -*-
import re

from django.http import HttpResponse, Http404
from django.shortcuts import redirect

from mongoengine.django.shortcuts import get_document_or_404

from documents import File

def file_view(request, file_id, transformation_name):
    file = get_document_or_404(File, id=file_id)
    try:
        modification = file.modifications[transformation_name]
    except File.DerivativeNotFound:
        if transformation_name.find('.') != -1:
            return redirect('/media/notfound/%s' % transformation_name)
        raise Http404()

    response = HttpResponse(modification.file.read(),
                            content_type=modification.file.content_type)
    response['Last-Modified'] = modification.file.upload_date
    return response

