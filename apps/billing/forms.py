# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import Tariff, AccessCamOrder


class TariffForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(max_length=500, widget=forms.Textarea, required=False)
    cost = forms.IntegerField()
    duration = forms.IntegerField()
    is_controlled = forms.BooleanField(required=False)


class AccessCamOrderForm(forms.Form):
    pass
