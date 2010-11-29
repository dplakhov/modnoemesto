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
from apps.social.documents import User


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
    return direct_to_template(request, 'billing/pay.html', {
        'service': settings.PKSPB_ID,
        'account': request.user.id,
    })


def operator(request):
    """Accepting payments using bank cards.
    """
    import logging
    LOG_FILENAME = '/tmp/modnoemesto_debug.log'
    logger = logging.getLogger("simple_example")
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler(LOG_FILENAME)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s:%(message)s")
    ch.setFormatter(formatter)
    logger.addHandler(ch)


    def before(request):
        if request.GET.get('duser', None) != settings.PKSPB_DUSER or\
           request.GET.get('dpass', None) != settings.PKSPB_DPASS or\
           request.GET.get('sid', None) != '1':
            logger.debug('1')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        cid = request.GET.get('cid', None)
        if not cid:
            logger.debug('2')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        try:
            user = User.objects.get(id=cid)
        except User.DoesNotExist:
            logger.debug('3')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_CID)
        return user

    def action_get_info(request, user):
        logger.debug('4')
        return HttpResponse('status=%i' % TRANS_STATUS.SUCCESSFUL)

    def get_pay_params(request):
        term = int(request.GET.get('term', None))
        trans = int(request.GET.get('trans', None))
        amount = float(request.GET.get('sum', None))
        if term and trans and amount:
            return term, trans, amount
        raise ValueError

    def action_prepayment(request, user):
        try:
            params = get_pay_params(request)
        except (ValueError, TypeError):
            logger.debug('5')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        order = UserOrder(user=user)
        order.term, order.trans, order.amount = params
        order.save()
        logger.debug('6')
        return HttpResponse('status=%i&summa=%.2f' % (TRANS_STATUS.SUCCESSFUL, order.amount))

    def action_payment(request, user):
        try:
            params = get_pay_params(request)
        except (ValueError, TypeError):
            logger.debug('7')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        term, trans, amount = params
        try:
            order = UserOrder.objects.get(user=user, trans=trans)
        except UserOrder.DoesNotExist:
            logger.debug('8')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)
        if (order.term, order.amount) == (term, amount):
            order.is_payed = True
            order.save()
            user.cash += order.amount
            user.save()
            logger.debug('9')
            return HttpResponse('status=%i&summa=%.2f' % (TRANS_STATUS.SUCCESSFUL, order.amount))
        logger.debug('10')
        return HttpResponse('status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def main(request):
        try:
            result = before(request)
            if type(result) == HttpResponse:
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
            logger.debug('11')
            return HttpResponse('status=%i' % TRANS_STATUS.INVALID_UACT)
        except:
            #@TODO: need log
            logger.debug('12')
            import sys, traceback
            logger.debug(traceback.format_exc())
            return HttpResponse('status=%i' % TRANS_STATUS.INTERNAL_SERVER_ERROR)

    logger.debug("="*80)
    logger.debug("GET  = %s" % repr(request.GET))
    logger.debug("POST = %s" % repr(request.POST))
    logger.debug("="*80)
    response = main(request)
    logger.debug(response.content)
    logger.debug("="*80)
    response = main(request)
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