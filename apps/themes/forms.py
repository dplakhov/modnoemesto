# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _


class ThemeAddForm(forms.Form):
    file = forms.FileField(_('Theme file'))
