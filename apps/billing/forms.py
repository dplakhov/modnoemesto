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

    meta = {
       #'indexes': ['-timestamp', 'author'],
       'ordering': ['name'],
   }



class AccessCamOrderForm(forms.Form):
    tariff = forms.ChoiceField(choices=())
    duration = forms.IntegerField(min_value=1)

    def __init__(self, user=None, camera_is_controlled=None, *args, **kwarg):
        super(AccessCamOrderForm, self).__init__(*args, **kwarg)
        self.user = user
        self.camera_is_controlled = camera_is_controlled
        self.fields['tariff'].choices = tuple((i.id, i.name) for i in Tariff.objects.only('id','name').all())

    def clean_tariff(self):
        tariff = Tariff.objects.get(id=self.cleaned_data['tariff'])
        if self.camera_is_controlled != tariff.is_controlled:
            raise forms.ValidationError(_(u"Ошибка выбора тарифа"))
        return tariff

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if 'tariff' in self.cleaned_data:
            tariff = self.cleaned_data['tariff']
            self.total_cost = tariff.cost * duration
            if self.total_cost > self.user.cash:
                raise forms.ValidationError(_(u"Не хватает модов"))
        return duration