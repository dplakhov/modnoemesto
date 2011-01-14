# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class InviteForm(forms.Form):
    name = forms.CharField(label=_("Friend name"),
                           max_length=50)
    email = forms.EmailField(label=_("Email"))

FILE_TYPE_CHOICES = (
    ('csv', _('CSV')),
    ('vcard', _('vCard'))
)

class ImportInviteForm(forms.Form):
    file = forms.FileField(_('File'))

    type = forms.ChoiceField(label=_('File type'),
                             widget=forms.RadioSelect,
                             choices=FILE_TYPE_CHOICES
                             )
  