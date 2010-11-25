from datetime import datetime
from mongoengine import *
from mongoengine import connection

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from auth import User
from django.core.urlresolvers import reverse


class LimitsViolationException(Exception):
    def __init__(self, cause):
        self.cause = cause
        super(LimitsViolationException, self).__init__()


class Account(User):
    groups = ListField(ReferenceField('Group'))

    # activation stuff
    activation_code = StringField(max_length=12)

    # subscriptions
    mutual_friends = ListField(ReferenceField('Account'))


    # some denormalisation
    friends_count = IntField(default=0)
    fs_offers_inbox_count = IntField(default=0)

    @property
    def messages(self):
        from apps.user_messages.documents import MessageBoxFactory
        return MessageBoxFactory(self)


    # some control
    version = IntField(default=0)

    avatar = ReferenceField('File')

    cash = IntField(default=0)

    hometown = StringField(max_length=30)
    birthday = StringField(max_length=10)
    sex = StringField(max_length=1)
    icq = StringField(max_length=30)
    mobile = StringField(max_length=30)
    website = URLField()
    university = StringField(max_length=30)
    department = StringField(max_length=30)
    status = StringField(max_length=30)

    meta = {
        'indexes': ['username', 'mutual_friends']
    }

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

            acc1, acc2 = Account.objects(id__in=(self.id, user.id)).only(
                'version', 'friends_count')

            for acc in (acc1, acc2):
                if acc.friends_count > 499:
                    raise LimitsViolationException(acc)

            FriendshipOffer.objects.get(recipient=self,
                                        author=user).delete(is_accepted=True)

            Account.objects(id=user.id).update_one\
                    (add_to_set__mutual_friends=self, inc__friends_count=1,
                     inc__version=1)
            Account.objects(id=self.id).update_one\
                    (add_to_set__mutual_friends=user, inc__friends_count=1,
                     dec__fs_offers_inbox_count=1, inc__version=1)
        else:
            #@warning: this code is non-transactional too
            _, created = FriendshipOffer.objects.get_or_create(recipient=user,
                                                    author=self)
            if created:
                Account.objects(id=user.id).update_one\
                    (inc__fs_offers_inbox_count=1, inc__version=1)

    def unfriend(self, user):
        #@todo: maybe move whole routine to some asynchronous worker such as
        # celery
        #@warning: this code is non-transactional

        # we don't need to check document versions, so let's just increment it
        Account.objects(id=self.id, mutual_friends=user
            ).update_one(pull__mutual_friends=user, inc__version=1,
                    dec__friends_count=1)
        Account.objects(id=user.id, mutual_friends=user
            ).update_one(pull__mutual_friends=self, inc__version=1,
                    dec__friends_count=1)

    def get_absolute_url(self):
        return reverse('social:user',  kwargs=dict(user_id=self.id))

<<<<<<< HEAD

    def avatar_micro(self):
        format = "%ix%i" % settings.AVATAR_SIZES[2]
        if self.avatar:
            return reverse('social:avatar',  kwargs=dict(user_id=self.id, format=format))
        else:
            return "/media/img/notfound/avatar_%s.png" % format


class Group(Document):
    name = StringField(required=True, unique=True)
    members = ListField(ReferenceField('Account'))

    def add_member(self, user):
        Group.objects(id=self.id).update_one(add_to_set__members=user)
        Account.objects(id=user.id).update_one(add_to_set__groups=self)

    def remove_member(self, user):
        Group.objects(id=self.id).update_one(pull__members=user)
        Account.objects(id=user.id).update_one(pull__groups=self)

=======
>>>>>>> 6a33961410a0f2c2dd20b923a54ad4c3c73716c8

class FriendshipOffer(Document):
    timestamp = DateTimeField()
    author = ReferenceField('Account')
    recipient = ReferenceField('Account')

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
            Account.objects(id=self.recipient.id).update_one\
                    (dec__fs_offers_inbox_count=1, inc__version=1)
        super(FriendshipOffer, self).delete()


