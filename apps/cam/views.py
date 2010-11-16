# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required

from mongoengine.django.shortcuts import get_document_or_404

from .models import Camera
from .models import CameraType

from .forms import CameraTypeForm, CameraForm
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

def cam_list(request):
    cams = Camera.objects()
    return direct_to_template(request, 'cam/cam_list.html', dict(cams=cams) )


@login_required
def cam_edit(request, id=None):
    if id:
        cam = get_document_or_404(Camera, id=id)
        initial = {}
        initial['name'] = cam.name
        initial['type'] = cam.type.id
        initial['ip'] = cam.ip
        initial['username'] = cam.username
        initial['password'] = cam.password

    else:
        cam = None
        initial = {}

    form = CameraForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not cam:
            cam = Camera()
            cam.owner = request.user

        cam.name = form.cleaned_data['name']
        cam.type = CameraType.objects.get(id=form.cleaned_data['type'])
        cam.ip = form.cleaned_data['ip']
        cam.username = form.cleaned_data['username']
        cam.password = form.cleaned_data['password']

        cam.save()
        return HttpResponseRedirect(reverse('cam:cam_list'))

    return direct_to_template(request, 'cam/cam_edit.html',
                              dict(form=form, is_new=id is None)
                              )



def cam_view(request, id):
    cam = get_document_or_404(Camera, id=id)
    return direct_to_template(request, 'cam/cam_view.html',
                              dict(cam=cam)
                              )



@login_required
def type_list(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_list.html',
                              dict(types=types)
                              )
@login_required
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
