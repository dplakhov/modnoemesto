# -*- coding: utf-8 -*-

from django import forms
#from wtforms.ext.mongoengine.orm import model_form
from .models import CameraType

class CameraTypeForm(forms.Form):
    name = forms.CharField()

class CameraForm(forms.Form):
    name = forms.CharField()
    type = forms.ChoiceField(choices=tuple([(x.id, x.name) for x in CameraType.objects.all()]))


#CameraTypeForm = model_form(CameraType)