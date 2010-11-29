# -*- coding: utf-8 -*-
from django.shortcuts import redirect

from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings

from apps.media.documents import File, FileSet

from apps.utils.image import read_image_file
from apps.utils.stringio import StringIO

from apps.media.transformations import BatchFileTransformation, ImageResize
from apps.media.tasks import apply_file_transformations

from .forms import ImageAddForm

from .constants import *

def get_library(type):
    assert type in (LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_AUDIO, LIBRARY_TYPE_VIDEO, )
    library, created = FileSet.objects.get_or_create(type='common_%s_library' % type)
    return library

def image_index(request):
    library = get_library(LIBRARY_TYPE_IMAGE)
    if request.user.is_superuser:
        form = ImageAddForm()
    else:
        form = None
    return direct_to_template(request, 'media_library/image_index.html',
                              dict(
                                      files=library.files,
                                      form=form,
                                   )
                              )

def image_add(request):
    form = ImageAddForm(request.POST, request.FILES)
    if form.is_valid():
        file = request.FILES['file']
        buffer = StringIO()

        for chunk in file.chunks():
            buffer.write(chunk)

        buffer.reset()
        try:
            read_image_file(buffer)
        except Exception, e:
            messages.add_message(request, messages.ERROR, _('Invalid image file format'))
        else:
            image = File(type=FILE_TYPE_IMAGE, author=request.user)
            buffer.reset()
            image.file.put(buffer, content_type=file.content_type)
            image.save()
            library = get_library(LIBRARY_TYPE_IMAGE)
            library.add_file(image)

            transformations = [ ImageResize(name=name, format='png', width=w, height=h)
                                    for (name, w, h) in (
                ('library_image_thumbnail.png', 200, 100),
                ('library_image_full.png', 400, 200),
            )]

            if settings.TASKS_ENABLED.get(LIBRARY_IMAGE_RESIZE_TASK):
                args = [ image.id, ] + transformations
                apply_file_transformations.apply_async(args=args)
            else:
                image.apply_transformations(*transformations)

            messages.add_message(request, messages.SUCCESS, _('Image successfully added'))

    return redirect('media_library:image_index')

def audio_index(request):
    return HttpResponse()

def video_index(request):
    return HttpResponse()

