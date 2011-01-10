# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from documents import Tariff, AccessCamOrder

from forms import TariffForm, AccessCamOrderForm
from apps.billing.models import UserOrder, UserId
from apps.cam.documents import Camera
from django.conf import settings
from apps.billing.constans import TRANS_STATUS, ACCESS_CAM_ORDER_STATUS
from apps.social.documents import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage
from apps.robokassa.forms import RobokassaForm



@permission_required('superuser')
def tariff_list(request):
    return direct_to_template(request, 'billing/tariff_list.html',
                              {'tariffs': Tariff.objects().only('id','name') } )


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


@permission_required('superuser')
def tariff_delete(request, id):
    get_document_or_404(Tariff, id=id).delete()
    return HttpResponseRedirect(reverse('billing:tariff_list'))


def purse(request):
    robokassa_form = RobokassaForm(initial={
                         'InvId': UserId.get_id_by_user(request.user),
                         'Desc': request.user,
                         'Email': request.user.email,
                     })
    return direct_to_template(request, 'billing/pay.html', {
        'service': settings.PKSPB_ID,
        'account': request.user.id,
        'robokassa_form': robokassa_form,
    })


def operator(request):
    """Accepting payments using bank cards.
    """
    #@TODO: fix KeyError
    from apps.groups.documents import Group


    def before(request):
        if request.GET.get('duser', None) != settings.PKSPB_DUSER or\
           request.GET.get('dpass', None) != settings.PKSPB_DPASS or\
           request.GET.get('sid', None) != '1':
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        cid = request.GET.get('cid', None)
        if not cid:
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        try:
            user = User.objects.get(id=cid)
        except User.DoesNotExist:
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_CID)
        return user

    def action_get_info(request, user):
        return HttpResponse('status=%i' % TRANS_STATUS.SUCCESSFUL)

    def get_pay_params(request):
        term = int(request.GET.get('term', None))
        if term < 0: raise ValueError
        trans = int(request.GET.get('trans', None))
        if trans < 0: raise ValueError
        amount = float(request.GET.get('sum', None))
        if amount < 0: raise ValueError
        if term and trans and amount:
            return term, trans, amount
        raise ValueError

    def action_payment(request, user):
        try:
            params = get_pay_params(request)
        except (ValueError, TypeError):
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        term, trans, amount = params
        trans_count = UserOrder.objects.filter(trans=trans).count()
        if trans_count > 0:
            return HttpResponse('status=%i' % TRANS_STATUS.ALREADY)
        order = UserOrder(
            user_id=user.id,
            term=term,
            trans=trans,
            amount=amount,
        )
        order.save()
        user.cash += order.amount
        user.save()
        return HttpResponse('status=%i&summa=%.2f' % (TRANS_STATUS.SUCCESSFUL, order.amount))

    def main(request):
        try:
            result = before(request)
            if type(result) == HttpResponse:
                return result
            if 'uact' not in request.GET:
                return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
            uactf = {
                'get_info': action_get_info,
                'payment': action_payment,
            }.get(request.GET['uact'])
            if uactf:
                return uactf(request, result)
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_UACT)
        except:
            #import sys, traceback
            return HttpResponse('status=%i' % TRANS_STATUS.INTERNAL_SERVER_ERROR)

    response = main(request)
    return response


def get_access_to_camera(request, id, is_controlled):
    camera = get_document_or_404(Camera, id=id)
    if request.POST:
        form = AccessCamOrderForm(is_controlled, request.user, request.POST)
        if form.is_valid():
            tariff = form.cleaned_data['tariff']
            if tariff.is_packet:
                order = AccessCamOrder.create_packet_type(
                    tariff=tariff,
                    count_packets=form.cleaned_data['duration'],
                    user=request.user,
                    camera=camera,
                )
            else:
                order = AccessCamOrder.create_time_type(
                    tariff=tariff,
                    user=request.user,
                    camera=camera,
                )
            camera.check_operator(order)
            return HttpResponseRedirect(reverse('social:user', args=[camera.owner.id]))
    else:
        form = AccessCamOrderForm(is_controlled)
    return direct_to_template(request, 'billing/get_access_to_camera.html', {'form':form})


@permission_required('superuser')
def order_list(request, page=1):
    q = UserOrder.objects.order_by('-timestamp').all()
    paginator = Paginator(q, 25)
    try:
        orders = paginator.page(page)
    except (EmptyPage, InvalidPage):
        orders = paginator.page(paginator.num_pages)
    return direct_to_template(request, 'billing/order_list.html', {'orders':orders})


@permission_required('superuser')
def access_order_list(request, page=1):
    q = AccessCamOrder.objects.order_by('-create_on').all()
    paginator = Paginator(q, 25)
    try:
        orders = paginator.page(page)
    except (EmptyPage, InvalidPage):
        orders = paginator.page(paginator.num_pages)
    return direct_to_template(request, 'billing/access_order_list.html', {'orders':orders})
