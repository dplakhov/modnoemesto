# -*- coding: utf-8 -*-
from apps.cam.documents import CameraTag
from apps.cam.forms import CameraTagForm
from apps.utils.paginator import paginate

from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.contrib import messages


from mongoengine.django.shortcuts import get_document_or_404

from .constants import AVAILABLE_COMMANDS

from .documents import Camera
from .documents import CameraType

from .forms import CameraTypeForm
from .forms import CamFilterForm
from .documents import CameraBookmarks


def cam_list(request):
    private_tags = ","["'%s'" % i.id for i in CameraTag.objects(is_private=True)]
    if request.GET:
        form = CamFilterForm(request.GET)
        if form.is_valid():
            data = dict(form.cleaned_data)
            if data['name']:
                data['name__icontains'] = data['name']
            del data['name']
            if data['tags']:
                data['tags'] = CameraTag.objects(id=data['tags']).first()
            else:
                if not request.user.is_view_private_cam:
                    public_tags = [i.id for i in CameraTag.objects(is_private=False)]
                    data.update(dict(tags__in=public_tags))
                del data['tags']
            if data['order']:
                order = data['order']
            else:
                order = None
            del data['order']
            if not data['is_managed']:
                del data['is_management_enabled']
                del data['is_management_public']
                del data['is_management_paid']
            for k, v in data.items():
                if not v: del data[k]
            cams = Camera.objects(**data)
            if order:
                try:
                    name, type = order.split('-')
                except ValueError:
                    name, type = 'popularity', 'desc'
                order = ''
                if name == 'time':
                    order = 'date_created'
                    if type == 'desc':
                        order = '-%s' % order
                if name == 'popularity':
                    order = 'view_count'
                    if type == 'desc':
                        order = '-%s' % order
                cams = cams.order_by(order)
            cams = paginate(request,
                            cams,
                            cams.count(),
                            12)
        else:
            cams = None
        if request.is_ajax():
            return direct_to_template(request, 'cam/_cameras.html', dict(cams=cams))
        else:
            return direct_to_template(request, 'cam/cam_list.html', dict(form=form,cams=cams,private_tags=private_tags))
    else:
        form = CamFilterForm()
        tags = []
        for tag in CameraTag.objects.order_by('-count')[:4]:
            cams = list(Camera.objects(tags=tag.id).order_by('-view_count')[:4])
            tags.append((tag, cams))
        return direct_to_template(request, 'cam/cam_list.html', dict(form=form,tags=tags,private_tags=private_tags) )


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


def cam_bookmarks(request, id=None):
    if id:
        user = get_document_or_404(User, id=id)
    else:
        user = request.user
    try:
        bookmarks = CameraBookmarks.objects.get(user=user)
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


def inc_view_count(request, id):
    if not request.is_ajax():
        return HttpResponseNotFound()
    Camera.objects(id=id).update_one(inc__view_count=1)
    return HttpResponse('OK')


def place_update(request, name, type):
    order = ''
    if name == 'time':
        order = 'date_created'
        if type == 'desc':
            order = '-%s' % order
    if name == 'popularity':
        order = 'view_count'
        if type == 'desc':
            order = '-%s' % order
    #request.places_all_count = Camera.objects.count()
    request.places = paginate(request,
                              Camera.objects(is_view_public=True, is_view_enabled=True).order_by(order),
                              Camera.objects(is_view_public=True, is_view_enabled=True).count(),
                              10,
                              reverse('cam:place_update', args=[name, type]))
    return direct_to_template(request, '_places.html')
