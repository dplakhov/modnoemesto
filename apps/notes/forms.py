# -*- coding: utf-8 -*-

from django import forms

class NoteForm(forms.Form):
    title = forms.CharField(max_length=128)
    text = forms.CharField(widget=forms.Textarea())
    is_public = forms.BooleanField(required=False)
