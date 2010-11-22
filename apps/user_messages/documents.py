# -*- coding: utf-8 -*-
from datetime import datetime
from mongoengine import *

class Message(Document):
    text = StringField(required=True)
    author = ReferenceField('Account')
    recipient = ReferenceField('Account')
    timestamp = DateTimeField()
    userlist = ListField(ReferenceField('Account'))
    is_read = BooleanField(default=False)
    sender_deleted = DateTimeField()
    recipient_deleted = DateTimeField()

    meta = {
        'indexes': [
                '-timestamp',
                'author',
                'recipient',
                'userlist',
                'sender_deleted',
                'recipient_deleted',
        ]
    }

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()


    def delete_from(self, user):
        from apps.social.documents import Account

        if user in self.userlist:
            place = 'msg_sent' if user == self.author else 'msg_inbox'
            cmd = { 'pull__%s' % place: self, 'dec__%s_count' % place: 1,
                    'inc__version': 1 }
            if not self.is_read and self.recipient.id == user.id:
                cmd['dec__unread_msg_count'] = 1
            Account.objects(id=user.id).update_one(**cmd)
            if len(self.userlist) > 1:
                Message.objects(id=self.id).update_one(pull__userlist=user)
            else:
                #@todo: ensure that we really don't need deleted messages
                self.delete()

