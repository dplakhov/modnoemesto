# -*- coding: utf-8 -*-
from django.shortcuts import redirect

from django.http import HttpResponse, Http404
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, InvalidPage

from apps.media.documents import File, FileSet

from apps.utils.image import read_image_file
from apps.utils.stringio import StringIO

from apps.media.transformations import BatchFileTransformation, ImageResize
from apps.media.tasks import apply_file_transformations

from .forms import ImageAddForm

from .constants import *
from django.contrib.auth.decorators import login_required, user_passes_test
from mongoengine.django.shortcuts import get_document_or_404

def get_library(type):
    assert type in (LIBRARY_TYPE_IMAGE, LIBRARY_TYPE_AUDIO, LIBRARY_TYPE_VIDEO, )
    library, created = FileSet.objects.get_or_create(type='common_%s_library' % type)
    return library

def can_manage_library(user):
    return user.has_perm('superuser')

#@login_required
def image_index(request):
    library = get_library(LIBRARY_TYPE_IMAGE)
    if can_manage_library(request.user):
        form = ImageAddForm()
    else:
        form = None

    paginator = Paginator(library.files, settings.LIBRARY_IMAGES_PER_PAGE)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        objects = paginator.page(page)
    except (EmptyPage, InvalidPage):
        objects = paginator.page(paginator.num_pages)

    return direct_to_template(request, 'media_library/image_index.html',
                              dict(
                                      objects=objects,
                                      form=form,
                                      can_manage=can_manage_library(request.user),
                                   )
                              )
@user_passes_test(can_manage_library)
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


@user_passes_test(can_manage_library)
def image_delete(request, id):
    library = get_library(LIBRARY_TYPE_IMAGE)
    image = get_document_or_404(File, id=id)
    library.remove_file(image)
    messages.add_message(request, messages.SUCCESS, _('Image successfully removed'))
    return redirect('media_library:image_index')


def audio_index(request):
    return HttpResponse()

def video_index(request):
    return HttpResponse()

