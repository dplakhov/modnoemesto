from django import forms
from apps.media.fields import ImageField


class PhotoForm(forms.Form):
    file = ImageField(label=_("Image"))