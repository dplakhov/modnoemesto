# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from .models import Camera
from .models import CameraType

def cam_list(request):
    cams = Camera.objects()
    return direct_to_template(request, 'cam/cam_list.html', dict(cams=cams) )

def cam_add(request):
    return direct_to_template(request, 'cam/cam_add.html', dict(cams=cams) )

def type_list(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_list.html',
                              dict(types=types)
                              )


def type_add(request):
    types = CameraType.objects()
    return direct_to_template(request, 'cam/type_add.html',
                              dict(types=types)
                              )

