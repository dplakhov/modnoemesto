# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import User
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email and password."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        # TODO: determine whether this should move to its own method.
        #if self.request:
        #    if not self.request.session.test_cookie_worked():
        #        raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username
    and password.
    """
    first_name = forms.CharField(label=_("First name"), max_length=64)
    last_name = forms.CharField(label=_("Last name"), max_length=64)
    phone = forms.CharField(label=_("Phone"), required=False)
    email = forms.EmailField(label=_("Email"))
    username = forms.CharField(label=_("Login"), max_length=64, required=False)
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, max_length=64)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, max_length=64)

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects(email=email).count():
            raise forms.ValidationError(_("A user with that email already"
                                          " exists."))
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't"
                                          " match."))
        return password2


class MessageTextForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea, required=True)


class ChangeAvatarForm(forms.Form):
    file = forms.FileField(label=_("Image"), required=True)


class ChangeProfileForm(forms.Form):
    SEX_CHOICES = (
        ('', _('None selected')),
        ('f', _('Female')),
        ('m', _('Male')),
    )

    hometown = forms.CharField(label=_("Hometown"), max_length=30, required=False)
    birthday = forms.CharField(label=_("Birthday"), max_length=10, required=False)
    sex = forms.ChoiceField(label=_("Sex"), choices=SEX_CHOICES, required=False)
    icq = forms.CharField(label=_("ICQ"), max_length=30, required=False)
    mobile = forms.CharField(label=_("Mobile"), max_length=30, required=False)
    website = forms.URLField(label=_("Website"), required=False)
    university = forms.CharField(label=_("University"), max_length=30, required=False)
    department = forms.CharField(label=_("Department"), max_length=30, required=False)
    university_status = forms.CharField(label=_("Status"), max_length=30, required=False)


class LostPassword(forms.Form):
    email = forms.EmailField(label=_("Email"))