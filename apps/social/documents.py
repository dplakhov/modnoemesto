from datetime import datetime
from mongoengine import *
from django.utils.hashcompat import md5_constructor, sha_constructor
from django.utils.encoding import smart_str

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from django.core.urlresolvers import reverse

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
    username = StringField(max_length=30, unique=True, required=True)
    first_name = StringField(max_length=30)
    last_name = StringField(max_length=30)
    email = StringField()
    password = StringField(max_length=128)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)
    is_superuser = BooleanField(default=False)
    last_login = DateTimeField(default=datetime.now)
    date_joined = DateTimeField(default=datetime.now)
    groups = ListField(ReferenceField('Group'))

    # activation stuff
    activation_code = StringField(max_length=12)

    # subscriptions
    mutual_friends = ListField(ReferenceField('User'))


    # some denormalisation
    friends_count = IntField(default=0)
    fs_offers_inbox_count = IntField(default=0)

    @property
    def messages(self):
        from apps.user_messages.documents import MessageBoxFactory
        return MessageBoxFactory(self)

    avatar = ReferenceField('File')

    cash = FloatField(default=0.0)

    profile = ReferenceField('Profile', required=True, unique=True, default=Profile)

    meta = {
        'indexes': ['username', 'mutual_friends']
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
    def create_user(cls, username, password, email=None):
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

        user = cls(username=username, email=email, date_joined=now)
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
        #@todo: bad fix KeyError
        from apps.billing.documents import Tariff
        return Camera.objects(owner=self).first()

    def friend(self, user):
        #@todo: maybe move whole routine to some asynchronous worker such as
        # celery
        if self.id == user.id:
            return
        if FriendshipOffer.objects(recipient=self, author=user).count():
            #@warning: this code is non-transactional
            # minor limits violation is possible due to requests concurrency

            acc1, acc2 = User.objects(id__in=(self.id, user.id)).only('friends_count')

            for acc in (acc1, acc2):
                if acc.friends_count > 499:
                    raise LimitsViolationException(acc)

            FriendshipOffer.objects.get(recipient=self,
                                        author=user).delete(is_accepted=True)

            User.objects(id=user.id).update_one\
                    (add_to_set__mutual_friends=self, inc__friends_count=1
                     )
            User.objects(id=self.id).update_one\
                    (add_to_set__mutual_friends=user, inc__friends_count=1,
                     dec__fs_offers_inbox_count=1)
        else:
            #@warning: this code is non-transactional too
            _, created = FriendshipOffer.objects.get_or_create(recipient=user,
                                                    author=self)
            if created:
                User.objects(id=user.id).update_one\
                    (inc__fs_offers_inbox_count=1)

    def unfriend(self, user):
        #@todo: maybe move whole routine to some asynchronous worker such as
        # celery
        #@warning: this code is non-transactional

        User.objects(id=self.id, mutual_friends=user
            ).update_one(pull__mutual_friends=user,
                    dec__friends_count=1)
        User.objects(id=user.id, mutual_friends=user
            ).update_one(pull__mutual_friends=self,
                    dec__friends_count=1)

    def get_absolute_url(self):
        return reverse('social:user',  kwargs=dict(user_id=self.id))

    def avatar_micro(self):
        format = "%ix%i" % settings.AVATAR_SIZES[2]
        if self.avatar:
            return reverse('social:avatar',  kwargs=dict(user_id=self.id, format=format))
        else:
            return "/media/img/notfound/avatar_%s.png" % format


class FriendshipOffer(Document):
    timestamp = DateTimeField()
    author = ReferenceField('User')
    recipient = ReferenceField('User')

    meta = {
        'indexes': ['-timestamp', 'author', 'recipient']
    }

    def __init__(self, *args, **kwargs):
        super(FriendshipOffer, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()

    def delete(self, is_accepted=False):
        """
        @param is_accepted: if False (default), also decreases recipient's
        fs_offers_inbox_count field value
        """
        if not is_accepted:
            User.objects(id=self.recipient.id).update_one\
                    (dec__fs_offers_inbox_count=1)
        super(FriendshipOffer, self).delete()