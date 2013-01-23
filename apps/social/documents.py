# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.encoding import smart_str

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from apps.utils.mail import send_mail
from django.template.loader import render_to_string

from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode

from apps.groups.documents import GroupUser
from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, URLField
from mongoengine.fields import BooleanField, DateTimeField, FloatField
from mongoengine.fields import ListField, DateTimeField
from apps.utils.decorators import cached_property



OFFLINE_TIMEDELTA = 300

class LimitsViolationException(Exception):
    def __init__(self, cause):
        self.cause = cause
        super(LimitsViolationException, self).__init__()



def get_hexdigest(algorithm, salt, raw_password):
    raw_password, salt = smart_str(raw_password), smart_str(salt)
    if algorithm == 'md5':
        return md5_constructor(salt + raw_password).hexdigest()
    elif algorithm == 'sha1':
        return sha_constructor(salt + raw_password).hexdigest()
    raise ValueError('Got unknown password algorithm type in password')


class Profile(Document):
    user = ReferenceField('User')
    is_active = BooleanField(default=False)

    hometown = StringField(max_length=30)
    birthday = StringField(max_length=10)
    sex = StringField(max_length=1)
    icq = StringField(max_length=30)

    mobile = StringField(max_length=30)
    website = URLField()

    university = StringField(max_length=30)
    department = StringField(max_length=30)
    university_status = StringField(max_length=30)

    get_news = BooleanField()

    announce = StringField(max_length=512,
                           default=unicode(_('No upcoming events')))

    inviter = ReferenceField('User')

    theme = ReferenceField('Theme')

    meta = {
        'indexes': [
            'user',
            'inviter',
        ]
    }

    def for_html(self):
        from apps.social.forms import ChangeProfileForm
        self.sex = dict(ChangeProfileForm.SEX_CHOICES).get(self.sex, ChangeProfileForm.SEX_CHOICES[0][1])
        if self.mobile:
            self.mobile = "+7 (%s) %s %s %s" % (self.mobile[:3], self.mobile[3:6], self.mobile[6:8], self.mobile[8:])
            self.mobile_code = self.mobile[:3]
            self.mobile_number = self.mobile[3:]
        return self


class User(Document):
    """A User document that aims to mirror most of the API specified by Django
    at http://docs.djangoproject.com/en/dev/topics/auth/#users
    """
    username = StringField(max_length=64)

    first_name = StringField(max_length=64)
    last_name = StringField(max_length=64)

    email = StringField(unique=True, required=True)

    phone = StringField(max_length=30)

    password = StringField(max_length=64)

    is_active = BooleanField(default=True)
    is_banned = BooleanField(default=False)

    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    last_login = DateTimeField(default=datetime.now)
    last_access = DateTimeField(default=datetime.now)
    date_joined = DateTimeField(default=datetime.now)

    permissions = ListField(StringField())

    activation_code = StringField(max_length=12)


    def gen_activation_code(self):
        from random import choice
        alpha = 'abcdef0123456789'
        self.activation_code = ''.join(choice(alpha) for _ in xrange(12))


    def send_activation_code(self):
        #@todo: send email in a separate process (queue worker or smth like it)
        #@todo: check email sending results
        email_body = render_to_string('emails/confirm_registration.txt',
                { 'user': self, 'SITE_DOMAIN': settings.SITE_DOMAIN })

        #if settings.DEBUG:
        #    print email_body

        if settings.SEND_EMAILS:
            send_mail(_('Confirm registration'), email_body,
            settings.SERVER_EMAIL, [self.email],
            fail_silently=True)


    def send_restore_password_code(self):
        email_body = render_to_string('emails/recovery_password.txt',
                        { 'user': self, 'SITE_DOMAIN': settings.SITE_DOMAIN })

        if settings.SEND_EMAILS:
            send_mail(_('Password Reset Request'), email_body,
            settings.SERVER_EMAIL, [self.email],
            fail_silently=True)


    @property
    def messages(self):
        from apps.user_messages.documents import MessageBoxFactory
        return MessageBoxFactory(self)

    avatar = ReferenceField('File')

    cash = FloatField(default=0.0)

    @property
    def profile(self):
        from apps.themes.documents import Theme
        return Profile.objects.get_or_create(user=self)[0]

    @cached_property
    def groups(self):
        return [i.group for i in GroupUser.objects(user=self, status=GroupUser.STATUS.ACTIVE).only('group')]

    @cached_property
    def administered_groups(self):
        return [i.group for i in GroupUser.objects(user=self,
                                                   status=GroupUser.STATUS.ACTIVE,
                                                   is_admin=True).only('group')]

    @cached_property
    def groups_invites(self):
        return [i.group for i in GroupUser.objects(user=self, status=GroupUser.STATUS.INVITE).only('group')]

    @cached_property
    def groups_requests(self):
        requests = []
        for i in GroupUser.objects(user=self, status=GroupUser.STATUS.ACTIVE, is_admin=True).only('group'):
            requests += GroupUser.objects(group=i.group, status=GroupUser.STATUS.REQUEST).all()
        return requests

    @cached_property
    def groups_events_count(self):
        invites = GroupUser.objects(user=self, status=GroupUser.STATUS.INVITE).count()
        for i in GroupUser.objects(user=self, status=GroupUser.STATUS.ACTIVE, is_admin=True).only('group'):
            invites += GroupUser.objects(group=i.group, status=GroupUser.STATUS.REQUEST).count()
        return invites

    @property
    def friends(self):
        from apps.friends.documents import UserFriends
        return UserFriends.objects.get_or_create(user=self)[0]

    @cached_property
    def friends_online(self):
        return filter(lambda x: x.is_online(), self.friends.list)

    meta = {
        'indexes': ['email', ]
    }

    def __unicode__(self):
        return smart_unicode(self.get_full_name() or self.username or str(self.id))

    def get_full_name(self):
        """Returns the users first and last names, separated by a space.
        """
        full_name = u'%s %s' % (self.first_name or '', self.last_name or '')
        return full_name.strip()

    def is_anonymous(self):
        return False

    def is_authenticated(self):
        return True

    def is_online(self):
        return User.get_delta_time() < self.last_access

    @staticmethod
    def users_online():
        return User.objects.filter(last_access__gt=User.get_delta_time())

    def set_offline(self):
        self.last_access = datetime.now() - timedelta(seconds=settings.CHAT_OFFLINE_TIMEDELTA)
        self.save()

    def set_online(self):
        self.last_access = datetime.now()
        self.save()

    @staticmethod
    def get_delta_time():
        return datetime.now() - settings.TIME_IS_ONLINE

    def set_password(self, raw_password):
        """Sets the user's password - always use this rather than directly
        assigning to :attr:`~mongoengine.django.auth.User.password` as the
        password is hashed before storage.
        """
        from random import random
        algo = 'sha1'
        salt = get_hexdigest(algo, str(random()), str(random()))[:5]
        hash = get_hexdigest(algo, salt, raw_password)
        self.password = '%s$%s$%s' % (algo, salt, hash)
        self.save()
        return self

    def check_password(self, raw_password):
        """Checks the user's password against a provided password - always use
        this rather than directly comparing to
        :attr:`~mongoengine.django.auth.User.password` as the password is
        hashed before storage.
        """
        algo, salt, hash = self.password.split('$')
        return hash == get_hexdigest(algo, salt, raw_password)

    @classmethod
    def create_user(cls, email, password, username=None, is_superuser=False, first_name='', last_name=''):
        """Create (and save) a new user with the given username, password and
        email address.
        """
        now = datetime.now()

        # Normalize the address by lowercasing the domain part of the email
        # address.
        if email is not None:
            try:
                email_name, domain_part = email.strip().split('@', 1)
            except ValueError:
                pass
            else:
                email = '@'.join([email_name, domain_part.lower()])

        user = cls(username=username, email=email, date_joined=now,
                   is_staff=is_superuser, is_superuser=is_superuser,
                   first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save()
        return user

    def get_and_delete_messages(self):
        return []

    def has_module_perms(self, perm):
        return self.has_perm(perm)

    def has_perm(self, perm):
        if self.is_superuser:
            return True

        if perm == 'superuser':
            return False

        return perm in self.get_all_permissions()

    def get_all_permissions(self):
        return self.permissions

    def get_camera(self):
        from apps.cam.documents import Camera
        return Camera.objects(owner=self).first()

    def get_absolute_url(self):
        return reverse('social:user', kwargs=dict(user_id=self.id))


class Setting(Document):
    name = StringField(unique=True, required=True)
    value = StringField()

    @staticmethod
    def is_started(value=None):
        def set_is_started(value):
            setting = Setting.objects.get_or_create(name='is_started', defaults={'value': 'false'})[0]
            setting.value = 'true' if value else 'false'
            setting.save()

        def get_is_started():
            setting = Setting.objects.get_or_create(name='is_started', defaults={'value': 'false'})[0]
            return setting.value == 'true'
        if value is None:
            return get_is_started()
        set_is_started(value)

