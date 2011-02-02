# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.admin import widgets as admin_widgets

from apps.groups.documents import GroupTheme, GroupType, Group

class GroupCreationForm(forms.Form):
    name = forms.CharField(label=_('Name'), max_length=255)
    description = forms.CharField(label=_('Description'),
                                  max_length=settings.GROUP_DESCRIPTION_MAX_LENGTH,
                                  widget=forms.Textarea, required=False)
    theme = forms.ChoiceField(label=_('Theme'), choices=(), required=False)
    type = forms.ChoiceField(label=_('Type'), choices=(), required=False)
    site = forms.URLField(label=_('Site'), required=False)
    country = forms.CharField(label=_('Country'), required=False)
    city = forms.CharField(label=_('City'), required=False)
    public = forms.BooleanField(label=_('Access'), required=False)
    has_video_conference = forms.BooleanField(label=_('Has video conference'),
                                              required=False)
    timestamp = forms.DateTimeField(label=_('Timestamp'), required=False,
                                    widget = admin_widgets.AdminSplitDateTime
                                    )

    def __init__(self, *args, **kwarg):
        initial = kwarg.get('initial')
        self.group_id = None
        if initial:
            if 'theme' in initial and initial['theme']:
                initial['theme'] = initial['theme'].id
            if 'type' in initial and initial['type']:
                initial['type'] = initial['type'].id
            if None in initial and initial[None]:
                self.group_id = initial[None]
        super(GroupCreationForm, self).__init__(*args, **kwarg)
        self.fields['theme'].choices = [('', _('none selected')),] + [(i.id, i.name) for i in GroupTheme.objects.only('id','name').all()]
        self.fields['type'].choices = [('', _('none selected')),] + [(i.id, i.name) for i in GroupType.objects.only('id','name').all()]

    def clean_name(self):
        name = self.cleaned_data['name']
        params = { 'name__iexact': name }
        if self.group_id:
            params['id__ne'] = self.group_id
        if Group.objects(**params).count() > 0:
            raise forms.ValidationError(_(u"Group with that name already exists"))
        return name

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


class MessageTextForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea, required=True)