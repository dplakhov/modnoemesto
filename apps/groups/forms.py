# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.groups.documents import GroupTheme, GroupType

class GroupCreationForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=255)
    description = forms.CharField(label=_('Description'), max_length=500, widget=forms.Textarea, required=False)
    theme = forms.ChoiceField(label=_('Theme'), choices=(), required=False)
    type = forms.ChoiceField(label=_('Type'), choices=(), required=False)
    site = forms.URLField(label=_('Site'), required=False)
    country = forms.CharField(label=_('Country'), required=False)
    city = forms.CharField(label=_('City'), required=False)
    public = forms.BooleanField(label=_('Access'), required=False)

    def __init__(self, *args, **kwarg):
        initial = kwarg.get('initial')
        if initial:
            if 'theme' in initial and initial['theme']:
                initial['theme'] = initial['theme'].id
            if 'type' in initial and initial['type']:
                initial['type'] = initial['type'].id
        super(GroupCreationForm, self).__init__(*args, **kwarg)
        self.fields['theme'].choices = [('', _('none selected')),] + [(i.id, i.name) for i in GroupTheme.objects.only('id','name').all()]
        self.fields['type'].choices = [('', _('none selected')),] + [(i.id, i.name) for i in GroupType.objects.only('id','name').all()]

    def clean_theme(self):
        if not self.cleaned_data['theme']:
            return
        theme = GroupTheme.objects(id=self.cleaned_data['theme']).first()
        if not theme:
            raise forms.ValidationError(_(u"Does Not Exist"))
        return theme

    def clean_type(self):
        if not self.cleaned_data['type']:
            return
        type = GroupType.objects(id=self.cleaned_data['type']).first()
        if not type:
            raise forms.ValidationError(_(u"Does Not Exist"))
        return type


class ThemeForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=255)


class TypeForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=255)