# -*- coding: utf-8 -*-
import os

from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.conf import settings

from documents import File

def file_view(request, transformation_name, file_id=None):
    not_found_path = '%snotfound/%s'
    converting_path = '%sconverting/%s'
    if file_id:
        try:
            file = File.objects.get(id=file_id)
        except File.DoesNotExist:
            file = None
            raise Http404()

        else:
            try:
                modification = file.modifications[transformation_name]
            except File.DerivativeNotFound:
                modification = None
    else:
        file = None
        modification = None

    if modification:
        response = HttpResponse(modification.file.read(),
                            content_type=modification.file.content_type)
        response['Last-Modified'] = modification.file.upload_date
        return response

    if file and os.path.exists(converting_path %
                    (settings.MEDIA_ROOT, transformation_name)):
        return redirect(converting_path %
                (settings.MEDIA_URL, transformation_name))


    if os.path.exists(not_found_path %
                    (settings.MEDIA_ROOT, transformation_name)):
        return redirect(not_found_path %
                    (settings.MEDIA_URL, transformation_name))

    raise Http404()