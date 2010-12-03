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

class Friendship(Document):
    friends = ListField(ReferenceField('User'))
    ctime = DateTimeField(default=datetime.now)


class UserFriends(Document):
    user = ReferenceField('User', unique=True)
    list = ListField(ReferenceField('User'))

    _offers = None

    @property
    def count(self):
        return 0

    def can_add(self, user):
        has_offers = FriendshipOffer.objects(sender=self.user, recipient=user).count()
        return not has_offers

    @property
    def offers(self):
        if self._offers is None:
            self._offers = FriendshipOfferList(self.user)
        return self._offers

    def friend(self, user):
        self.user.friends.add(user)
        user.friends.add(self.user)

    def add(self, user):
        self.list.append(user)
        UserFriends.objects(user=self.user).update_one(push__list=user)


