# -*- coding: utf-8 -*-
from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.core.urlresolvers import reverse

from mongoengine.django.shortcuts import get_document_or_404

from documents import Tariff, AccessCamOrder

from forms import TariffForm, AccessCamOrderForm
from apps.billing.models import UserOrder
from apps.cam.documents import Camera
from django.conf import settings
from apps.billing.constans import TRANS_STATUS


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
    order = UserOrder(user=request.user)
    order.save()
    return direct_to_template(request, 'billing/pay.html', {
        'service': settings.PKSPB_ID,
        'account': order.id,
    })


def operator(request):
    """Accepting payments using bank cards.
    """
    def before(request):
        if request.GET.get('duser', None) != settings.PKSPB_DUSER or\
           request.GET.get('dpass', None) != settings.PKSPB_DPASS or\
           request.GET.get('sid', None) != '1':
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        cid = request.GET.get('cid', '')
        if not cid or not cid.isdigit():
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        try:
            order = UserOrder.objects.get(id=cid)
        except UserOrder.DoesNotExist:
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_CID)
        return order

    def action_get_info(request, order):
        return HttpResponse('status=%i' % TRANS_STATUS.SUCCESSFUL)

    def get_pay_params(request):
        term = int(request.GET.get('term', None))
        trans = int(request.GET.get('trans', None))
        amount = float(request.GET.get('sum', None))
        if term and trans and amount:
            return term, trans, amount
        raise ValueError

    def action_prepayment(request, order):
        try:
            params = get_pay_params(request)
        except (ValueError, TypeError):
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        order.term, order.trans, order.amount = params
        order.save()
        return HttpResponse('status=%i&summa=%.2f' % (TRANS_STATUS.SUCCESSFUL, order.amount))

    def action_payment(request, order):
        try:
            params = get_pay_params(request)
        except (ValueError, TypeError):
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        if (order.term, order.trans, order.amount) == params:
            return HttpResponse('status=%i&summa=%.2f' % (TRANS_STATUS.SUCCESSFUL, order.amount))
        return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def main(request):
        try:
            result = before(request)
            if type(result) != UserOrder:
                return result
            if 'uact' not in request.GET:
                return HttpResponseNotFound()
            uactf = {
                'get_info': action_get_info,
                'prepayment': action_prepayment,
                'payment': action_payment,
            }.get(request.GET['uact'])
            if uactf:
                return uactf(request, result)
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_UACT)
        except:
            #@TODO: need log
            return HttpResponse('status=%i' % TRANS_STATUS.INTERNAL_SERVER_ERROR)

    #print "="*80
    #print "GET  = %s" % repr(request.GET)
    #print "POST = %s" % repr(request.POST)
    #print "="*80
    response = main(request)
    #print response.content
    #print "="*80
    return response


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
            if not camera_is_controlled:
                order.set_access_period(form.cleaned_data['tariff'])
                request.user.cash -= form.total_cost
                request.user.save()
            order.save()
            return HttpResponseRedirect(reverse('social:user', args=[camera.owner.id]))
    else:
        form = AccessCamOrderForm()
    return direct_to_template(request, 'billing/get_access_to_camera.html', {'form':form})