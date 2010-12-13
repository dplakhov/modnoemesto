# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib import messages

from mongoengine.django.shortcuts import get_document_or_404

from .constants import AVAILABLE_COMMANDS

from .documents import Camera
from .documents import CameraType

from .forms import CameraTypeForm, CameraForm
from apps.billing.documents import Tariff
from apps.cam.forms import CamFilterForm, ScreenForm
from apps.cam.documents import CameraBookmarks
from django.shortcuts import redirect
from ImageFile import Parser as ImageFileParser


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from django.contrib import messages
from apps.media.documents import File
from apps.media.transformations.image import ImageResize
from apps.media.tasks import apply_file_transformations


def cam_list(request):
    form = CamFilterForm(request.POST or None)
    if form.is_valid():
        data = dict(form.cleaned_data)
        if not data['name']:
            del data['name']
        else:
            data['name__icontains'] = data['name']
            del data['name']
        if not data['is_managed']:
            del data['is_management_enabled']
            del data['is_management_public']
            del data['is_management_paid']
        cams = Camera.objects(**data)
    else:
        cams = Camera.objects(is_view_public=True,
                                is_view_enabled=True).order_by('-date_created')

    return direct_to_template(request, 'cam/cam_list.html', dict(form=form,cams=cams) )


def cam_edit(request, id=None):
    user = request.user
    if id:
        cam = get_document_or_404(Camera, id=id)
        if not user.is_superuser and user.id != cam.owner.id:
            return HttpResponseNotFound()
        initial = cam._data
        initial['type'] = cam.type.get_option_value()
        for tariff_type in Camera.TARIFF_FIELDS:
            value = getattr(cam, tariff_type)
            if value:
                initial[tariff_type] = value.id

    else:
        cam = None
        initial = {}

    form = CameraForm(user, request.POST or None, initial=initial)

    if form.is_valid():
        if not cam:
            cam = Camera()
            cam.owner = user

        for k, v in form.cleaned_data.items():
            setattr(cam, k, v)

        cam.type = CameraType.objects.get(id=form.cleaned_data['type'][:-2])

        for tariff_type in Camera.TARIFF_FIELDS:
            value = form.cleaned_data[tariff_type]
            if value:
                value = Tariff.objects.get(id=value)
                assert value in getattr(Tariff, 'get_%s_list' % tariff_type)()
                setattr(cam, tariff_type, value)
            else:
                setattr(cam, tariff_type, None)

        cam.save()

        return HttpResponseRedirect(reverse('social:home'))

    return direct_to_template(request, 'cam/cam_edit.html',
                              dict(form=form, is_new=id is None)
                              )


def screen(request, cam_id, format):
    camera = get_document_or_404(Camera, id=cam_id)
    if not camera.screen:
        return redirect('/media/img/notfound/screen_%s.png' % format)

    try:
        image = camera.screen.get_derivative(format)
    except File.DerivativeNotFound:
        return redirect('/media/img/converting/screen_%s.png' % format)

    response = HttpResponse(image.file.read(), content_type=image.file.content_type)
    response['Last-Modified'] = image.file.upload_date
    return response


def screen_edit(request, id=None):
    if id:
        camera = get_document_or_404(Camera, id=id)
        if not request.user.is_superuser and request.user.id != camera.owner.id:
            return HttpResponseNotFound()
    else:
        camera = request.user.get_camera()
        if not camera:
            return redirect('social:home')

    if request.method != 'POST':
        form = ScreenForm()
    else:
        form = ScreenForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            buffer = StringIO()

            for chunk in file.chunks():
                buffer.write(chunk)

            buffer.reset()
            try:
                parser = ImageFileParser()
                parser.feed(buffer.read())
                image = parser.close()
                image_valid = True
            except Exception, e:
                messages.add_message(request, messages.ERROR, _('Invalid image file format'))
                image_valid = False

            if image_valid:
                screen = File(type='image')
                buffer.reset()
                screen.file.put(buffer, content_type=file.content_type)
                screen.save()

                camera.screen = screen
                camera.save()

                transformations = [ ImageResize(name='%sx%s' % (w,h), format='png', width=w, height=h)
                                    for (w, h) in settings.SCREEN_SIZES ]

                if settings.TASKS_ENABLED.get('SCREEN_RESIZE'):
                    args = [ screen.id, ] + transformations
                    apply_file_transformations.apply_async(args=args)
                else:
                    screen.apply_transformations(*transformations)

                messages.add_message(request, messages.SUCCESS, _('Screen successfully updated'))
                return HttpResponseRedirect(request.path)


    return direct_to_template(request, 'cam/screen_edit.html',
                              dict(form=form, camera=camera)
                              )


def cam_view(request, id):
    cam = get_document_or_404(Camera, id=id)
    return direct_to_template(request, 'cam/cam_view.html',
                              dict(cam=cam)
                              )



@permission_required('superuser')
def type_list(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_list.html',
                              dict(types=types)
                              )


@permission_required('superuser')
def type_edit(request, id=None):
    if id:
        type = get_document_or_404(CameraType, id=id)
        initial = type._data
    else:
        type = None
        initial = {}

    form = CameraTypeForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not type:
            type = CameraType()

        for k, v in form.cleaned_data.items():
            if k.startswith('_'):
                continue
            if hasattr(type, k):
                setattr(type, k, v)
        type.save()
        #return HttpResponseRedirect(reverse('cam:type_edit', kwargs=dict(id=type.id)))
        return HttpResponseRedirect(reverse('cam:type_list'))

    return direct_to_template(request, 'cam/type_edit.html',
                              dict(form=form, is_new=id is None)
                              )


@permission_required('superuser')
def type_delete(request, id):
    type = get_document_or_404(CameraType, id=id)
    type.delete()
    return HttpResponseRedirect(reverse('cam:type_list'))


def cam_manage(request, id, command):
    if command not in AVAILABLE_COMMANDS:
        return HttpResponseNotFound()

    cam = get_document_or_404(Camera, id=id)
    cam = Camera()

    return HttpResponse()


def cam_bookmarks(request):
    try:
        bookmarks = CameraBookmarks.objects.get(user=request.user)
    except CameraBookmarks.DoesNotExist:
        cameras = None
    else:
        cameras = bookmarks.cameras
    return direct_to_template(request, 'cam/bookmarks.html', {'cameras': cameras})


def cam_bookmark_add(request, id):
    camera = get_document_or_404(Camera, id=id)
    camera.bookmark_add(request.user)
    messages.add_message(request, messages.SUCCESS,
                             _('Bookmark successfully added'))
    return redirect(reverse('social:user', args=[camera.owner.id]))


def cam_bookmark_delete(request, id):
    camera = get_document_or_404(Camera, id=id)
    camera.bookmark_delete(request.user)
    messages.add_message(request, messages.SUCCESS,
                             _('Bookmark successfully deleted'))
    return redirect(reverse('social:user', args=[camera.owner.id]))