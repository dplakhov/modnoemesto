# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class GroupCreationForm(forms.Form):
    name = forms.CharField(label=_("Name"), max_length=255)
