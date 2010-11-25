# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _

class NoteForm(forms.Form):
    title = forms.CharField(label=_('Title'), max_length=128)
    text = forms.CharField(label=_('Text'), widget=forms.Textarea())
    is_public = forms.BooleanField(label=_('Is public'), required=False)
