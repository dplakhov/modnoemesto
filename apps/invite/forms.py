# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class InviteForm(forms.Form):
    name = forms.CharField(label=_("Friend name"),
                           max_length=50)
    email = forms.EmailField(label=_("Email"))


class ImportInviteForm(forms.Form):
    file = forms.FileField(_('File'), widget=forms.FileInput(attrs={'size': 40}))

