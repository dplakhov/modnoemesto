# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import Tariff, AccessCamOrder
from apps.billing.models import UserOrder


class TariffForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(max_length=500, widget=forms.Textarea, required=False)
    cost = forms.IntegerField()
    duration = forms.IntegerField()
    is_controlled = forms.BooleanField(required=False)


class AccessCamOrderForm(forms.Form):
    pass


class UserOrderForm(forms.ModelForm):
    total = forms.IntegerField(min_value=1)
    class Meta:
        model = UserOrder
        fields = ('total',)
