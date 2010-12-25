from django import forms
from apps.media.fields import ImageField
from django.utils.translation import ugettext_lazy as _


class PhotoForm(forms.Form):
    file = ImageField(label=_("Image"))