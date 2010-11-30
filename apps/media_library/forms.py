# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class ImageAddForm(forms.Form):
    file = forms.FileField(label=_("Image"), required=True)
    title = forms.CharField(label=_("Title"), required=True)
    description = forms.CharField(label=_("Description"), required=True)

