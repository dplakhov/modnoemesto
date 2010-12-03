# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine.document import Document
from mongoengine.fields import ReferenceField, StringField, BooleanField, DateTimeField, ListField

from apps.social.documents import User

class FriendshipOffer(Document):
    author = ReferenceField('User')
    recipient = ReferenceField('User')
    ctime = DateTimeField(default=datetime.now)
    message = StringField()

    meta = {
        'indexes': ['author', 'recipient']
    }

class Friendship(Document):
    friends = ListField(ReferenceField('User'))
    ctime = DateTimeField(default=datetime.now)


class UserFriends(Document):
    user = ReferenceField('User', unique=True)
    friends = ListField(ReferenceField('User'))

    @property
    def count(self):
        return 0

    def can_add(self, user):
        return True

    def offer_send(self, user, message=''):
        FriendshipOffer.objects.get_or_create(author=self.user,
                                       recipient=user,
                                       message=message
                                       )
