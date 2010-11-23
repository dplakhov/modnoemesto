# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

class MessageTextForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea, required=True)
