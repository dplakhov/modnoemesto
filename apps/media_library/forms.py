# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class MediaAddForm(forms.Form):
    title = forms.CharField(label=_("Title"), required=True)
    description = forms.CharField(label=_("Description"), required=True)

class ImageAddForm(MediaAddForm):
    file = forms.FileField(label=_("Image"), required=True)

class VideoAddForm(MediaAddForm):
    file = forms.FileField(label=_("Video"), required=True)
