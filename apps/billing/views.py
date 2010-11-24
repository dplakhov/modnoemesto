# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from documents import Tariff, AccessCamOrder

from forms import TariffForm, AccessCamOrderForm
from assist.decorators import cp1251
from assist.forms import AssistMode2Form
from apps.billing.models import UserOrder
from apps.billing.forms import UserOrderForm
from django.shortcuts import get_object_or_404
from apps.cam.models import Camera
from datetime import datetime


@login_required
@permission_required('superuser')
def tariff_list(request):
    return direct_to_template(request, 'billing/tariff_list.html',
                              {'tariffs': Tariff.objects().only('id','name') } )


@login_required
@permission_required('superuser')
def tariff_edit(request, id=None):
    if id:
        tariff = get_document_or_404(Tariff, id=id)
        initial = tariff._data
    else:
        tariff = None
        initial = {}

    form = TariffForm(request.POST or None, initial=initial)

    if form.is_valid():
        if not tariff:
            tariff = Tariff()

        for k, v in form.cleaned_data.items():
            setattr(tariff, k, v)

        tariff.save()
        return HttpResponseRedirect(reverse('billing:tariff_list'))

    return direct_to_template(request, 'billing/tariff_edit.html',
                              {'form':form, 'is_new':id is None})


@login_required
@permission_required('superuser')
def tariff_delete(request, id):
    get_document_or_404(Tariff, id=id).delete()
    return HttpResponseRedirect(reverse('billing:tariff_list'))


@login_required
def purse(request):
    if request.POST:
        form = UserOrderForm(request.POST)
        if form.is_valid():
            form.user = request.user.id
            order = form.save()
            return HttpResponseRedirect(reverse('billing:pay', args=[order.id]))
    else:
        form = UserOrderForm()
    return direct_to_template(request, 'billing/purse.html', {'form': form})


@login_required
@cp1251
def pay(request, order_id):
    MOD_COST = 30
    order = get_object_or_404(UserOrder, id=order_id)
    total_cost = order.total * MOD_COST
    form = AssistMode2Form(initial={
               'Order_IDP': order.id,
               'Subtotal_P': total_cost,
               'Comment': 'UserID: %r, Total mods: %r, Total cost: %r'  % (request.user.id, order.total, total_cost),
               'LastName': request.user.last_name,
               'FirstName': request.user.first_name,
               'Email': request.user.email,
               #'Phone': request.user.get_profile().phone,
           })
    # for tests:
    order.is_payed = True
    order.save()
    request.user.cash += order.total
    request.user.save()
    return direct_to_template(request, 'billing/pay.html', {'form':form, 'order':order, 'mod_cost':MOD_COST, 'total_cost':total_cost})


@login_required
def get_access_to_camera(request, id):
    camera = get_document_or_404(Camera, id=id)
    camera_is_controlled = camera.type.is_controlled
    if request.POST:
        form = AccessCamOrderForm(request.user, camera_is_controlled,request.POST)
        if form.is_valid():
            order = AccessCamOrder(
                tarif=form.cleaned_data['tariff'],
                duration=form.cleaned_data['duration'],
                user=request.user,
                camera=camera,
            )
            if camera_is_controlled:
                order.status = 'wait'
            else:
                order.status = 'enable'
                order.init_on = datetime.now()
                request.user.cash -= form.total_cost
                request.user.save()
            order.save()
            return HttpResponseRedirect(reverse('social:user', args=[camera.owner.id]))
    else:
        form = AccessCamOrderForm()
    return direct_to_template(request, 'billing/get_access_to_camera.html', {'form':form})