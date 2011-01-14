# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class InviteForm(forms.Form):
    name = forms.CharField(label=_("Friend name"),
                           max_length=50)
    email = forms.EmailField(label=_("Email"))

  