#coding: utf-8
from django.http import HttpResponse
from django.views.generic.simple import direct_to_template

from django.views.decorators.csrf import csrf_exempt

from .conf import USE_POST
from .forms import ResultURLForm, SuccessRedirectForm, FailRedirectForm
from apps.billing.models import UserOrder
from apps.social.documents import User


@csrf_exempt
def receive_result(request):
    """ обработчик для ResultURL. """
    data = request.POST if USE_POST else request.GET
    form = ResultURLForm(data)
    if form.is_valid():
        trans = form.cleaned_data['InvId']
        sum = form.cleaned_data['OutSum']
        
        extra_params = form.extra_params()
        user_id = extra_params['user_id']

        # сохраняем данные об успешном уведомлении в базе, чтобы
        # можно было выполнить дополнительную проверку на странице успешного
        # заказа
        user = User.objects.filter(id=user_id).first()
        if not user:
            return HttpResponse('error: bad user_id')
        order = UserOrder(
            user_id=user.id,
            amount=float(sum),
            trans=trans,
        )
        order.save()
        user.cash += order.amount
        user.save()

        return HttpResponse('OK%s' % trans)
    return HttpResponse('error: bad signature')


@csrf_exempt
def success(request, template_name='robokassa/success.html', extra_context=None,
            error_template_name = 'robokassa/error.html'):
    """ обработчик для SuccessURL """

    data = request.POST if USE_POST else request.GET
    form = SuccessRedirectForm(data)
    if form.is_valid():
        id, sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']
        context = {'InvId': id, 'OutSum': sum, 'form': form}
        context.update(form.extra_params())
        context.update(extra_context or {})
        return direct_to_template(request, template_name, extra_context=context)

    return direct_to_template(request, error_template_name, extra_context={'form': form})


@csrf_exempt
def fail(request, template_name='robokassa/fail.html', extra_context=None,
         error_template_name = 'robokassa/error.html'):
    """ обработчик для FailURL """

    data = request.POST if USE_POST else request.GET
    form = FailRedirectForm(data)
    if form.is_valid():
        id, sum = form.cleaned_data['InvId'], form.cleaned_data['OutSum']
        context = {'InvId': id, 'OutSum': sum, 'form': form}
        context.update(form.extra_params())
        context.update(extra_context or {})
        return direct_to_template(request, template_name, extra_context=context)

    return direct_to_template(request, error_template_name, extra_context={'form': form})

