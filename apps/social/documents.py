# -*- coding: utf-8 -*-

from datetime import datetime
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.encoding import smart_str

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse
from apps.groups.documents import GroupUser
from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, URLField, BooleanField, DateTimeField, FloatField
from apps.utils.decorators import cached_property

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
    hometown = StringField(max_length=30)
    birthday = StringField(max_length=10)
    sex = StringField(max_length=1)
    icq = StringField(max_length=30)
    mobile = StringField(max_length=30)
    website = URLField()
    university = StringField(max_length=30)
    department = StringField(max_length=30)
    university_status = StringField(max_length=30)


class User(Document):
    """A User document that aims to mirror most of the API specified by Django
    at http://docs.djangoproject.com/en/dev/topics/auth/#users
    """
    username = StringField(max_length=64)
    full_name = StringField(max_length=90)
    first_name = StringField(max_length=64)
    last_name = StringField(max_length=64)
    email = StringField(unique=True, required=True)
    phone = StringField(max_length=30)
    password = StringField(max_length=64)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    last_login = DateTimeField(default=datetime.now)
    last_access = DateTimeField(default=datetime.now)
    date_joined = DateTimeField(default=datetime.now)

    # activation stuff
    activation_code = StringField(max_length=12)

    @property
    def messages(self):
        from apps.user_messages.documents import MessageBoxFactory
        return MessageBoxFactory(self)

    avatar = ReferenceField('File')

    cash = FloatField(default=0.0)

    @property
    def profile(self):
        return Profile.objects.get_or_create(user=self)[0]

    @cached_property
    def groups(self):
        return [i.group for i in GroupUser.objects(user=self, is_invite=False).only('group')]

    @cached_property
    def groups_invite(self):
        return [i.group for i in GroupUser.objects(user=self, is_invite=True).only('group')]

    @property
    def friends(self):
        from apps.friends.documents import UserFriends
        return UserFriends.objects.get_or_create(user=self)[0]

    @cached_property
    def friends_online(self):
        return filter(lambda x: x.is_online(),self.friends.list)
        
    meta = {
        'indexes': ['username',]
    }


    def __unicode__(self):
        return self.username if self.username else ''

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
    def create_user(cls, username, password, email=None, is_superuser=False):
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

        user = cls(username=username, email=email, date_joined=now, is_superuser=is_superuser)
        user.set_password(password)
        user.save()
        return user

    def get_and_delete_messages(self):
        return []

    def has_perm(self, perm):
        if perm == 'superuser':
            return self.is_superuser
        raise Exception

    def get_camera(self):
        from apps.cam.documents import Camera
        return Camera.objects(owner=self).first()

    def get_absolute_url(self):
        return reverse('social:user',  kwargs=dict(user_id=self.id))

    def avatar_micro(self):
        format = "%ix%i" % settings.AVATAR_SIZES[2]
        if self.avatar:
            return reverse('social:avatar',  kwargs=dict(user_id=self.id, format=format))
        else:
            return "/media/img/notfound/avatar_%s.png" % format


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

