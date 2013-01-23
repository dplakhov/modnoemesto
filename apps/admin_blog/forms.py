# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class AdminBlogForm(forms.Form):
    title = forms.CharField(label=_('Title'), max_length=128)
    text = forms.CharField(label=_('Text'), widget=forms.Textarea(
            attrs=dict(rows="10", cols="40")))

       