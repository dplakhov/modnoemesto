# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, DateTimeField, ListField

class FriendshipOffer(Document):
    author = ReferenceField('User')
    recipient = ReferenceField('User')
    ctime = DateTimeField(default=datetime.now)
    message = StringField()

    meta = {
        'indexes': ['author', 'recipient']
    }

class FriendshipOfferList(object):
    def __init__(self, user):
        self.user = user

    def send(self, user, message=''):
        offer, created = FriendshipOffer.objects.get_or_create(author=self.user,
                                       recipient=user,
                                       defaults=dict(message=message)
                                       )



class Friendship(Document):
    friends = ListField(ReferenceField('User'))
    ctime = DateTimeField(default=datetime.now)


class UserFriends(Document):
    user = ReferenceField('User', unique=True)
    friends = ListField(ReferenceField('User'))

    _offers = None

    @property
    def count(self):
        return 0

    def can_add(self, user):
        has_offers = FriendshipOffer.objects(author=self.user, recipient=user).count()
        return not has_offers

    @property
    def offers(self):
        if self._offers is None:
            self._offers = FriendshipOfferList(self.user)
        return self._offers


