# -*- coding: utf-8 -*-
from apps.cam.documents import CameraTag
from apps.cam.forms import CameraTagForm

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings


from mongoengine.django.shortcuts import get_document_or_404

from .constants import AVAILABLE_COMMANDS

from .documents import Camera
from .documents import CameraType

from .forms import CameraTypeForm, CameraForm
from apps.billing.documents import Tariff
from .forms import CamFilterForm
from apps.media.forms import PhotoForm
from .documents import CameraBookmarks

from apps.social.documents import User


def cam_list(request):
    if request.POST:
        form = CamFilterForm(request.POST)
        if form.is_valid():
            data = dict(form.cleaned_data)
            if data['name']:
                data['name__icontains'] = data['name']
            del data['name']
            if data['tags']:
                data['tags'] = CameraTag.objects(id=data['tags']).first()
            else:
                del data['tags']
            if not data['is_managed']:
                del data['is_management_enabled']
                del data['is_management_public']
                del data['is_management_paid']
            for k, v in data.items():
                if not v: del data[k]
            cams = Camera.objects(**data)
        else:
            cams = []
        return direct_to_template(request, 'cam/cam_list.html', dict(form=form,cams=cams))
    else:
        form = CamFilterForm()
        tags = []
        for tag in CameraTag.objects.order_by('-count')[:4]:
            cams = list(Camera.objects(is_view_public=True,
                                       is_view_enabled=True,
                                       tags=tag.id).order_by('date_created')[:4])
            tags.append((tag, cams))
        return direct_to_template(request, 'cam/cam_list.html', dict(form=form,tags=tags) )


def cam_edit(request, id=None):
    user = request.user
    if id:
        cam = get_document_or_404(Camera, id=id)
        if not user.is_superuser and user.id != cam.owner.id:
            return HttpResponseNotFound()
        initial = cam._data
        initial['type'] = cam.type.get_option_value()
        initial['operator'] = initial['operator'] and initial['operator'].id
        initial['tags'] = initial['tags'] and [i.id for i in initial['tags']]
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
        cam.operator = form.cleaned_data['operator'] and User.objects(id=form.cleaned_data['operator']).first() or None
        if form.cleaned_data['tags']:
            new_tags = CameraTag.objects(id__in=form.cleaned_data['tags'])
            new_tag_ids = [i.id for i in new_tags]
            for old_tag in cam.tags:
                if old_tag in new_tag_ids:
                    new_tag_ids.remove(old_tag)
                else:
                    CameraTag.objects(id=old_tag).update_one(dec__count=1)
            for new_tag in new_tag_ids:
                CameraTag.objects(id=new_tag).update_one(inc__count=1)
            cam.tags = new_tags

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
                              dict(form=form, camera=cam)
                              )


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
        form = PhotoForm()
    else:
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            camera.screen = form.fields['file'].save('camera_screen', settings.SCREEN_SIZES, 'CAM_SCREEN_RESIZE')
            camera.save()
            messages.add_message(request, messages.SUCCESS, _('Screen successfully updated'))
            return HttpResponseRedirect(request.path)
    return direct_to_template(request, 'cam/screen_edit.html',
                              dict(form=form, screen=camera.screen)
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



@permission_required('superuser')
def tag_list(request):
    tags = CameraTag.objects()
    return direct_to_template(request, 'cam/tag_list.html',
                              dict(tags=tags)
                              )


@permission_required('superuser')
def tag_edit(request, id=None):
    if id:
        tag = get_document_or_404(CameraTag, id=id)
        initial = tag._data
    else:
        tag = None
        initial = {}

    form = CameraTagForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not tag:
            tag = CameraTag()

        for k, v in form.cleaned_data.items():
            if k.startswith('_'):
                continue
            if hasattr(tag, k):
                setattr(tag, k, v)
        tag.save()
        return HttpResponseRedirect(reverse('cam:tag_list'))

    return direct_to_template(request, 'cam/tag_edit.html',
                              dict(form=form, is_new=id is None)
                              )


@permission_required('superuser')
def tag_delete(request, id):
    tag = get_document_or_404(CameraTag, id=id)
    tag.delete()
    return HttpResponseRedirect(reverse('cam:tag_list'))


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