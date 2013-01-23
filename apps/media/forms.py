from django import forms
from .fields import ImageField, VideoField
from django.utils.translation import ugettext_lazy as _


class PhotoForm(forms.Form):
    file = ImageField(label=_("Image"))

class VideoForm(forms.Form):
    file = VideoField(label=_("Video"))
