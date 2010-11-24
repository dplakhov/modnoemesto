# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Camera, CameraType
from .drivers.base import Driver as BaseDriver
from .drivers.exceptions import ImproperlyConfigured, AccessDenied
from apps.billing.documents import Tariff


class CameraTypeForm(forms.Form):
    name = forms.CharField()
    driver = forms.CharField()

    def clean_driver(self):
        driver = self.cleaned_data['driver']
        camera_type = CameraType(driver=driver)
        try:
            driver_class = camera_type.driver_class
            assert issubclass(driver_class, BaseDriver)
        except:
            raise forms.ValidationError(_('Invalid driver name %(driver)s' % dict(driver=driver)))
        return driver


class CameraForm(forms.Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=())
    host = forms.CharField()
    username = forms.CharField()
    password = forms.CharField()
    enabled = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    paid = forms.BooleanField(required=False)
    operator = forms.ChoiceField(required=False, choices=())
    tariffs =  forms.MultipleChoiceField(choices=())

    def __init__(self, user, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = tuple(
                            (x.id, x.name) for x in CameraType.objects.all())
        self.fields['operator'].choices = [(user.username, 'myself'),] +\
            [(x.username, x.username) for x in user.mutual_friends]
        self.fields['tariffs'].choices = [(x.id, x.name) for x in Tariff.objects.all()]

    def tmp_disabled_clean(self):
        data = self.cleaned_data
        args = dict([(x, data[x]) for x in 'name host username password'.split()])
        args['type'] = CameraType.objects.get(id=data['type'])
        cam = Camera(**args)
        try:
            cam.driver.control.check()
        except AccessDenied:
            raise forms.ValidationError(_('Invalid camera credentials'))
        except ImproperlyConfigured:
            raise forms.ValidationError(_('Camera improperly configured'))
        return self.cleaned_data


class CamFilterForm(forms.Form):
    name = forms.CharField(required=False,label=u'Ключевые слова', widget=forms.TextInput(attrs={'class':'kay'}))
    enabled = forms.BooleanField(required=False,initial=True,label=u'Активные')
    public = forms.BooleanField(required=False,initial=True,label=u'Публичные')
    paid = forms.BooleanField(required=False,initial=False,label=u'Платные')