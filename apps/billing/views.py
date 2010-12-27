# -*- coding: utf-8 -*-
from datetime import timedelta
import urllib
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth import SESSION_KEY
from django.utils.importlib import import_module

from mongoengine.django.shortcuts import get_document_or_404

from documents import Tariff, AccessCamOrder

from forms import TariffForm, AccessCamOrderForm
from apps.billing.models import UserOrder
from apps.cam.documents import Camera
from django.conf import settings
from apps.billing.constans import TRANS_STATUS, ACCESS_CAM_ORDER_STATUS
from apps.social.documents import User
from django.core.paginator import Paginator, EmptyPage, InvalidPage


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
    return direct_to_template(request, 'billing/pay.html', {
        'service': settings.PKSPB_ID,
        'account': request.user.id,
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
            order = AccessCamOrder(
                tariff=tariff,
                duration=form.cleaned_data['duration'],
                user=request.user,
                camera=camera,
            )
            order.set_access_period(order.is_controlled)
            if tariff.is_packet:
                request.user.cash -= form.total_cost
                request.user.save()
            order.cost = form.total_cost
            order.save()
            if order.is_controlled:
                if order.status == ACCESS_CAM_ORDER_STATUS.ACTIVE:
                    camera.operator = request.user
                    camera.save()

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


def cam_view_notify(request):
    def calc():
        session_key = request.GET.get('session_key', None)
        order_id = request.GET.get('order_id', None)
        extra_time = request.GET.get('time', None)
        if not (session_key and order_id and extra_time):
            return 'BAD PARAMS',-1
        if not extra_time.isdigit():
            return 'BAD TIME', -2
        extra_time = int(extra_time)
        if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
            return 'BAD TIME', -2
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            return 'BAD SESSION KEY', -3
        user = User.objects(id=user_id).first()
        if not user:
            return 'BAD SESSION KEY', -3
        order = AccessCamOrder.objects(id=order_id).first()
        if not order:
            return 'DOES NOT EXIST ORDER', -4
        if order.user != user:
            return 'BAD USER', -5
        if order.end_date or order.tariff.is_packet:
            return 'BAD ORDER', -6
        total_cost = order.tariff.cost * (settings.TIME_INTERVAL_NOTIFY - extra_time)
        user.cash -= total_cost
        user.save()
        return 'OK', 0, float(user.cash)/order.tariff.cost
    result = calc()
    result = ["%s=%s" % (k, urllib.quote(str(v))) for k, v in zip(('info', 'status', 'cash'), result)]
    return HttpResponse('&'.join(result))
