# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class ImageAddForm(forms.Form):
    file = forms.FileField(label=_("Image"), required=True)

