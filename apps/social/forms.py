# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import User
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"), max_length=30)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))

        # TODO: determine whether this should move to its own method.
        if self.request:
            if not self.request.session.test_cookie_worked():
                raise forms.ValidationError(_("Your Web browser doesn't appear to have cookies enabled. Cookies are required for logging in."))
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
    full_name = forms.CharField(label=_("Full name"), max_length=90)
    phone = forms.CharField(label=_("Phone"), required=False)
    email = forms.EmailField(label=_("Email"), help_text = _("Please enter a"
        "valid email address, it is required to complete registration process"))
    username = forms.RegexField(label=_("Login"), max_length=30,
        regex=r'^[\w.@+-]+$', help_text = _("Required. 30 characters or fewer."
                                        " Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters,"
                                       " numbers and @/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput, help_text = _("Enter the same password as"
                                                  " above, for verification."))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects(username=username).count():
            raise forms.ValidationError(_("A user with that username already"
                                          " exists."))
        return username

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
