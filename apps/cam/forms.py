# -*- coding: utf-8 -*-
from apps.cam.documents import CameraTag
from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.billing.documents import Tariff

from .documents import Camera, CameraType
from .drivers.base import Driver as BaseDriver
from .drivers.exceptions import ImproperlyConfigured, AccessDenied


class CameraTypeForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    driver = forms.ChoiceField(label=_('Driver name'), initial='apps.cam.drivers.axis.AxisDriver')
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

    def __init__(self, *args, **kwargs):
        super(CameraTypeForm, self).__init__(*args, **kwargs)

        self.fields['driver'].choices = tuple(
                [('', _('Select camera driver'))] +
                    [
                        ('apps.cam.drivers.%s' % x, x)
                        for x in [
                            'axis.AxisDriver',
                            ]
                    ]
                )


class CameraTagForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    is_private = forms.BooleanField(label=_('Is private'), required=False)


class CameraForm(forms.Form):
    name = forms.CharField(label=_('Name'))
    type = forms.ChoiceField(label=_('Camera type'))
    tags = forms.MultipleChoiceField(label=_('Camera tags'))

    screen = forms.FileField(label=_("Image"), required=False)

    stream_name = forms.CharField(label=_('Stream name'), required=False)

    camera_management_host = forms.CharField(label=_('Camera management host'),
                                             required=False)
    camera_management_username = forms.CharField(label=_('Camera management username'),
                                                 required=False)
    camera_management_password = forms.CharField(label=_('Camera management password'),
                                                 required=False)

    is_view_enabled = forms.BooleanField(label=_('Is view enabled'), required=False)
    is_view_public = forms.BooleanField(label=_('Is view public'), required=False)
    is_view_paid = forms.BooleanField(label=_('Is view paid'), required=False)

    is_management_enabled = forms.BooleanField(label=_('Is management enabled'), required=False)
    is_management_public = forms.BooleanField(label=_('Is management public'),
                                              required=False)
    is_management_paid = forms.BooleanField(label=_('Is management paid'),
                                            required=False)

    management_packet_tariff =  forms.ChoiceField(label=_('Management packet tariff'),
                                                  required=False)
    management_time_tariff =  forms.ChoiceField(label=_('Management time tariff'),
                                                required=False)
    view_packet_tariff =  forms.ChoiceField(label=_('View packet tariff'),
                                            required=False)
    view_time_tariff =  forms.ChoiceField(label=_('View time tariff'),
                                          required=False)

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
        
        self.fields['operator'].choices = [('', _('None')), (user.id, user),] + [(x.id, x) for x in user.friends.list]
        self.fields['tags'].choices = [(x.id, x.name) for x in CameraTag.objects]

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
    tags = forms.ChoiceField(required=False, label=_('Camera tags'))
    order = forms.ChoiceField(required=False, choices=(
        ('popularity-desc', u'по популярности ↓'),
        ('popularity-asc', u'по популярности ↑'),
        ('time-desc', u'по времени добавления ↓'),
        ('time-asc', u'по времени добавления ↑'),
    ))

    is_view_enabled = forms.BooleanField(required=False, initial=False,
                                         label=_('View Enabled'))
    is_view_public = forms.BooleanField(required=False, initial=False,
                                        label=_('View Public'))
    is_view_paid = forms.BooleanField(required=False, initial=False,
                                      label=_('View Paid'))

    is_managed = forms.BooleanField(required=False, initial=False,
                                    label=_('Managed'))

    is_management_enabled = forms.BooleanField(required=False, initial=False,
                                               label=_('Management Enabled'))
    is_management_public = forms.BooleanField(required=False, initial=False,
                                              label=_('Management Public'))
    is_management_paid = forms.BooleanField(required=False, initial=False,
                                            label=_('Management Paid'))

    def __init__(self, *args, **kwargs):
        super(CamFilterForm, self).__init__(*args, **kwargs)
        self.fields['tags'].choices = [('', _('Camera tag'))] + [(x.id, x.name) for x in CameraTag.objects]
