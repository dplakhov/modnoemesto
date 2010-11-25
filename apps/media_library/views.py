# -*- coding: utf-8 -*-
from django.shortcuts import redirect

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ImageFile import Parser as ImageFileParser

from django.http import HttpResponse
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from apps.media.documents import File, FileSet

from .forms import ImageAddForm


LIBRARY_TYPE_IMAGE = 'image'
LIBRARY_TYPE_AUDIO = 'audio'
LIBRARY_TYPE_VIDEO = 'video'

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
            parser = ImageFileParser()
            parser.feed(buffer.read())
            parser.close()
        except Exception, e:
            messages.add_message(request, messages.ERROR, _('Invalid image file format'))
        else:
            image = File(type='image', author=request.user)
            buffer.reset()
            image.file.put(buffer, content_type=file.content_type)
            image.save()
            library = get_library(LIBRARY_TYPE_IMAGE)
            library.add_file(image)
            messages.add_message(request, messages.SUCCESS, _('Image successfully added'))

    return redirect('media_library:image_index')

def audio_index(request):
    return HttpResponse()

def video_index(request):
    return HttpResponse()

