from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import Account

class LoginForm(forms.Form):
    username = forms.CharField(max_length=128, required=True)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)


class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username
    and password.
    """
    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-]+$', help_text = _("Required. 30 characters or fewer."
                                        " Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters,"
                                       " numbers and @/./+/-/_ characters.")})
    email = forms.EmailField(label=_("Email"), help_text = _("Please enter a"
        "valid email address, it is required to complete registration process"))
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput, help_text = _("Enter the same password as"
                                                  " above, for verification."))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if Account.objects(username=username).count():
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
