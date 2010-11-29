# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from .constants import AVAILABLE_COMMANDS

from .documents import Camera
from .documents import CameraType

from .forms import CameraTypeForm, CameraForm
from apps.billing.documents import Tariff
from apps.cam.forms import CamFilterForm

@login_required
def cam_list(request):
    form = CamFilterForm(request.POST or None)
    if form.is_valid():
        data = dict(form.cleaned_data)
        if not data['name']:
            del data['name']
        else:
            data['name__icontains'] = data['name']
            del data['name']
        cams = Camera.objects(**data)
    else:
        cams = Camera.objects()
    return direct_to_template(request, 'cam/cam_list.html', dict(form=form,cams=cams) )

def is_superuser(user):
    return user.is_superuser

@login_required
def cam_edit(request, id=None):
    user = request.user
    if id:
        cam = get_document_or_404(Camera, id=id, owner=user)
        if not is_superuser(user) and user.id != cam.owner.id:
            return HttpResponseNotFound()
        initial = cam._data
        initial['type'] = cam.type.id
        initial['tariffs'] = cam.tariffs and [i.id for i in cam.tariffs] or []
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
            
        cam.type = CameraType.objects.get(id=form.cleaned_data['type'])

        cam.tariffs = Tariff.objects(id__in=form.cleaned_data['tariffs'])

        cam.save()
        return HttpResponseRedirect(reverse('social:home'))

    return direct_to_template(request, 'cam/cam_edit.html',
                              dict(form=form, is_new=id is None)
                              )


@login_required
def cam_view(request, id):
    cam = get_document_or_404(Camera, id=id)
    return direct_to_template(request, 'cam/cam_view.html',
                              dict(cam=cam)
                              )



@user_passes_test(is_superuser)
def type_list(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_list.html',
                              dict(types=types)
                              )

@user_passes_test(is_superuser)
def type_edit(request, id=None):
    if id:
        type = get_document_or_404(CameraType, id=id)
        initial = {}
        for k in type._fields.keys():
            if k in ('id', ):
                continue
            initial[k] = getattr(type, k)
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


@user_passes_test(is_superuser)
def type_delete(request, id):
    type = get_document_or_404(CameraType, id=id)
    type.delete()
    return HttpResponseRedirect(reverse('cam:type_list'))

@login_required
def cam_manage(request, id, command):
    if command not in AVAILABLE_COMMANDS:
        return HttpResponseNotFound()

    cam = get_document_or_404(Camera, id=id)
    cam = Camera()

    return HttpResponse()
