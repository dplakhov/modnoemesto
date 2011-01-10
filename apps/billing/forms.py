# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import Tariff, AccessCamOrder
from apps.billing.models import UserOrder


class TariffForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(max_length=500, widget=forms.Textarea, required=False)
    cost = forms.FloatField()
    duration = forms.IntegerField(required=False)
    is_controlled = forms.BooleanField(required=False)


class AccessCamOrderForm(forms.Form):
    tariff = forms.ChoiceField(choices=())
    duration = forms.IntegerField(min_value=1, required=False)

    def __init__(self, is_controlled, user=None, *args, **kwarg):
        super(AccessCamOrderForm, self).__init__(*args, **kwarg)
        self.user = user
        self.is_controlled = is_controlled
        self.fields['tariff'].choices = tuple((i.id, i.name) for i in Tariff.objects(is_controlled=is_controlled).only('id','name').all())

    def clean_tariff(self):
        return Tariff.objects.get(id=self.cleaned_data['tariff'])

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if 'tariff' in self.cleaned_data:
            tariff = self.cleaned_data['tariff']
            if tariff.is_packet:
                total_cost = tariff.cost * duration
                if total_cost > self.user.cash:
                    raise forms.ValidationError(_(u"Не хватает денег на оплату тарифа"))
        return duration

    def clean(self):
        if 'tariff' in self.cleaned_data:
            tariff = self.cleaned_data['tariff']
            if tariff.is_packet and 'duration' not in self.cleaned_data:
                raise forms.ValidationError(_(u"Для пакетного тарифа нужно указать продолжительность"))