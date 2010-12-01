# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.utils.translation import ugettext_lazy as _

from .documents import Camera, CameraType
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
    name = forms.CharField(label=_('Name'))
    type = forms.ChoiceField(label=_('Camera type'), choices=())
    stream_name = forms.CharField(label=_('Stream name'))
    host = forms.CharField(label=_('Host'))
    username = forms.CharField(label=_('Username'))
    password = forms.CharField(label=_('Password'))
    managed = forms.BooleanField(label=_('Enabled'), required=False)
    enabled = forms.BooleanField(label=_('Enabled'), required=False)
    public = forms.BooleanField(label=_('Public'), required=False)
    paid = forms.BooleanField(label=_('Paid'), required=False)
    operator = forms.ChoiceField(label=_('Operator'), required=False, choices=())
    tariffs =  forms.MultipleChoiceField(label=_('Tariffs'), choices=())

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
    name = forms.CharField(required=False, label=_('Keywords'),
                           widget=forms.TextInput(attrs={'class':'kay'}))
    enabled = forms.BooleanField(required=False, initial=True, label=_('Enableds'))
    public = forms.BooleanField(required=False, initial=True, label=_('Publics'))
    paid = forms.BooleanField(required=False, initial=False, label=_('Paids'))