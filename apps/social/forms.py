# -*- coding: utf-8 -*-
from apps.media.fields import ImageField
from django import forms
from django.utils.translation import ugettext_lazy as _

from documents import User
from django.contrib.auth import authenticate
from apps.supercaptcha import CaptchaField


GENDER_CHOICES = (
    ('', _(u'Не выбран')),
    ('m', _(u'Male')),
    ('f', _(u'Female')),
)

class PeopleFilterForm(forms.Form):
    first_name = forms.CharField(label=_(u"Имя"), required=False)
    last_name = forms.CharField(label=_(u"Фамилия"), required=False)
    birthday = forms.CharField(label=_(u"День рождения"), required=False)
    icq = forms.CharField(label=_(u"ICQ"), required=False)
    mobile = forms.CharField(label=_(u"Сотовый телефон"), required=False)
    website = forms.CharField(label=_(u"Сайт"), required=False)
    gender = forms.CharField(label=_(u"Пол"),
        widget=forms.Select(choices=GENDER_CHOICES,
                            #attrs={'class':'gender-selectbox'}
        ),
        required=False)
    city = forms.CharField(label=_(u"Город"), required=False)
    university_name = forms.CharField(label=_(u"Университет"), required=False)
    university_department = forms.CharField(label=_(u"Факультет"), required=False)
    university_status = forms.CharField(label=_(u"Статус"), required=False)
    is_online = forms.BooleanField(label=_(u'На сайте'), required=False, initial=True)
    has_photo = forms.BooleanField(label=_(u'C фото'), required=False)

    def clean_first_name(self):
        return self.cleaned_data["first_name"].strip()

    def clean_last_name(self):
        return self.cleaned_data["last_name"].strip()


class LoginForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct email and password."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError("inactive")

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


class PhoneNumberMultiWidget(forms.MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            forms.TextInput(attrs={'size':'3', 'maxlength':'3'}),
            forms.TextInput(attrs={'size':'7', 'maxlength':'7'}),
        )
        super(PhoneNumberMultiWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return value.split('-')
        return (None, None)

    def value_from_datadict(self, data, files, name):
        value = [u'', u'']
        # look for keys like name_1, get the index from the end
        # and make a new list for the string replacement values
        for d in filter(lambda x: x.startswith(name), data):
            index = int(d[len(name) + 1:])
            value[index] = data[d]
        if value[0] == value[1] == u'':
            return None
        return u'%s-%s' % tuple(value)


class UserCreationForm(forms.Form):
    """
    A form that creates a user, with no privileges, from the given username
    and password.
    """
    NAME_REGEXP = ur'^[A-zА-я\'\`\-]+$'
    first_name = forms.RegexField(label=_("First name"),
                                  regex=NAME_REGEXP,
                                  min_length=4,
                                  max_length=64,
                                  error_messages={'invalid': _("This value may contain only letters, numbers and '/`/- characters.")})
    last_name = forms.RegexField(label=_("Last name"),
                                 regex=NAME_REGEXP,
                                 min_length=4,
                                 max_length=64,
                                 error_messages={'invalid': _("This value may contain only letters, numbers and ./-/_/@/!/#/$/%/^/&/+/= characters.")})
    email = forms.EmailField(label=_("Email"), max_length=64)
    phone = forms.RegexField(label=_("Phone"),
                             required=False,
                             regex=r'^\d{3}-\d{7}$',
                             widget=PhoneNumberMultiWidget,
                             error_messages={'invalid': _("Phone number is invalid or can not be used. Check your spelling. For example: +7 916 3564334")})
    password1 = forms.RegexField(label=_("Password"),
                                 widget=forms.PasswordInput,
                                 min_length=4,
                                 max_length=64,
                                 regex=r'^[\w\.\-_@!#$%^&+=]+$',
                                 error_messages={'invalid': _("This value may contain only letters, numbers and ./-/_/@/!/#/$/%/^/&/+/= characters.")})
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, max_length=64)

    captcha = CaptchaField(label=_('Captcha'))


    def clean_phone(self):
        return self.cleaned_data["phone"].replace('-', '')

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        user = User.objects(email=email).only('is_active').first()
        if user:
            if user.is_active:
                raise forms.ValidationError(_("A user with that email already"
                                              " exists."))
            else:
                raise forms.ValidationError("inactive")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", None)
        password2 = self.cleaned_data["password2"]
        if password1 is not None and password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't"
                                          " match."))
        return password2


class MessageTextForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea, required=True)


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
    announce = forms.CharField(label=_("Announce"), max_length=512,
                               required=True, widget=forms.Textarea)
    get_news = forms.BooleanField(label=_("Get news"), required=False, initial=True)


class LostPasswordForm(forms.Form):
    email = forms.EmailField(label=_("Email"))


class SetNewPasswordForm(forms.Form):
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput, max_length=64)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput, max_length=64)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1", "")
        password2 = self.cleaned_data["password2"]
        if password1 != password2:
            raise forms.ValidationError(_("The two password fields didn't"
                                          " match."))
        return password2

