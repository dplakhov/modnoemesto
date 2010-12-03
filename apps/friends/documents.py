# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, DateTimeField, ListField, BooleanField

class FriendshipOffer(Document):
    sender = ReferenceField('User')
    recipient = ReferenceField('User')
    ctime = DateTimeField(default=datetime.now)
    message = StringField()
    changed = DateTimeField()
    accepted = BooleanField()
    rejected = BooleanField()

    meta = {
        'indexes': ['sender', 'recipient']
    }

class FriendshipOfferList(object):
    def __init__(self, user):
        self.user = user

    def send(self, user, message=''):
        if self.has_from_user(user):
            self.accept(user)
        else:
            offer, created = FriendshipOffer.objects.get_or_create(sender=self.user,
                                       recipient=user,
                                       defaults=dict(message=message)
                                       )

    @property
    def sent(self):
        return FriendshipOffer.objects(sender=self.user, changed=None)

    @property
    def incoming(self):
        return FriendshipOffer.objects(recipient=self.user, changed=None)

    def accept(self, user):
        FriendshipOffer.objects(sender=user, recipient=self.user).update_one(set__accepted=True,
                                                                             set__changed=datetime.now())
        self.user.friends.friend(user)

    def has_from_user(self, user):
        return FriendshipOffer.objects(sender=user, recipient=self.user, changed=None).count() != 0

    def has_for_user(self, user):
        return FriendshipOffer.objects(sender=self.user, recipient=user, changed=None).count() != 0


class UserFriends(Document):
    user = ReferenceField('User', unique=True)
    list = ListField(ReferenceField('User'))

    _offers = None

    @property
    def count(self):
        return len(self.list)

    def can_add(self, user):
        return not (self.contains(user) or self.offers.has_for_user(user))

    @property
    def offers(self):
        if self._offers is None:
            self._offers = FriendshipOfferList(self.user)
        return self._offers

    def contains(self, user):
        return user in self.list

    def friend(self, user):
        self._add(user)
        user.friends._add(self.user)

    def unfriend(self, user):
        self._remove(user)
        user.friends._remove(self.user)

    def _remove(self, user):
        self.list.remove(user)
        UserFriends.objects(user=self.user).update_one(pop__list=user)

    def _add(self, user):
        self.list.append(user)
        UserFriends.objects(user=self.user).update_one(push__list=user)

class Friendship(Document):
    friends = ListField(ReferenceField('User'))
    ctime = DateTimeField(default=datetime.now)

