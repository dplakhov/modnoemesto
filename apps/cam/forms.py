# -*- coding: utf-8 -*-

from itertools import chain

from django import forms
from django.utils.translation import ugettext_lazy as _

from .documents import Camera, CameraType
from .drivers.base import Driver as BaseDriver
from .drivers.exceptions import ImproperlyConfigured, AccessDenied
from apps.billing.documents import Tariff


class CameraTypeForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    driver = forms.CharField(label=_('Driver name'))
    is_controlled = forms.BooleanField(label=_('Is controlled'), required=False)

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

    camera_management_host = forms.CharField(label=_('Camera management host'))
    camera_management_username = forms.CharField(label=_('Camera management username'))
    camera_management_password = forms.CharField(label=_('Camera management password'))

    is_view_enabled = forms.BooleanField(label=_('Is view enabled'), required=False)
    is_view_public = forms.BooleanField(label=_('Is view public'), required=False)
    is_view_paid = forms.BooleanField(label=_('Is view paid'), required=False)

    is_management_enabled = forms.BooleanField(label=_('Is management enabled'), required=False)
    is_management_public = forms.BooleanField(label=_('Is management public'), required=False)
    is_management_paid = forms.BooleanField(label=_('Is management paid'), required=False)

    management_packet_tariff =  forms.ChoiceField(label=_('Management packet tariff'), required=False)
    management_time_tariff =  forms.ChoiceField(label=_('Management time tariff'), required=False)
    view_packet_tariff =  forms.ChoiceField(label=_('View packet tariff'), required=False)
    view_time_tariff =  forms.ChoiceField(label=_('View time tariff'), required=False)

    operator = forms.ChoiceField(label=_('Operator'), required=False)

    force_html5 = forms.BooleanField(label=_('Force html5'), required=False)

    def __init__(self, user, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = tuple(
                [('', _('Select camera type'))] +
                [
                            (x.get_option_value(), x.get_option_label())
                                   for x in CameraType.objects.all()
                ]
                            )
        
        self.fields['operator'].choices = [(user.username, 'myself'),] +\
            [(x.username, x.username) for x in user.mutual_friends]

        for tariff_type in Camera.TARIFF_FIELDS:
            self.fields[tariff_type].choices = tuple([('', _('Select tariff'))] +
                                 [(x.id, x.name)
                                 for x in getattr(Tariff,
                                      'get_%s_list' % tariff_type)()])


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