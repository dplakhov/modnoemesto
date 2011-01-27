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
    count_packets = forms.IntegerField(min_value=1, required=False)

    def __init__(self, camera, is_controlled, user=None, *args, **kwarg):
        super(AccessCamOrderForm, self).__init__(*args, **kwarg)
        self.user = user
        tariffs = []
        if is_controlled:
            tariffs.append(camera.management_packet_tariff)
            tariffs.append(camera.management_time_tariff)
        else:
            tariffs.append(camera.view_packet_tariff)
            tariffs.append(camera.view_time_tariff)
        self.fields['tariff'].choices = [(i.id, i.name) for i in tariffs if i]

    def clean_tariff(self):
        return Tariff.objects.get(id=self.cleaned_data['tariff'])

    def clean_count_packets(self):
        count_packets = self.cleaned_data['count_packets']
        if 'tariff' in self.cleaned_data:
            tariff = self.cleaned_data['tariff']
            if tariff.is_packet and not count_packets:
                raise forms.ValidationError(_(u"Для пакетного тарифа нужно указать продолжительность"))
            if tariff.is_packet:
                total_cost = tariff.cost * count_packets
                if total_cost > self.user.cash:
                    raise forms.ValidationError(_(u"Не хватает денег на оплату тарифа"))
        return count_packets