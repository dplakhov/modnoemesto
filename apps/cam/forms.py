# -*- coding: utf-8 -*-

from django import forms
#from wtforms.ext.mongoengine.orm import model_form
from .models import CameraType

class CameraTypeForm(forms.Form):
    name = forms.CharField()
    driver = forms.CharField()

class CameraForm(forms.Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=())
    host = forms.CharField()
    username = forms.CharField()
    password = forms.CharField()
    enabled = forms.BooleanField(required=False)
    public = forms.BooleanField(required=False)
    free = forms.BooleanField(required=False)

    def __init__(self, *args, **kwargs):
        super(CameraForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = tuple(
                            (x.id, x.name) for x in CameraType.objects.all())


#CameraTypeForm = model_form(CameraType)