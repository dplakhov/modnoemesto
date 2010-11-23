# -*- coding: utf-8 -*-
from datetime import datetime
from mongoengine import *
from django.conf import settings

from .tasks import message_store_set_readed

class MessageBox(object):

    def __init__(self, owner):
        self.owner = owner

    @property
    def _messages(self):
        raise NotImplementedError()
        return Message.objects.none()

    def __len__(self):
        return len(self._messages)

    def __iter__(self):
        return self._messages

    def __getitem__(self, item):
        return self._messages[item]

class IncomingMessageBox(MessageBox):
    @property
    def _messages(self):
        return Message.objects(recipient=self.owner)

class SentMessageBox(MessageBox):
    @property
    def _messages(self):
        return Message.objects(sender=self.owner)

class UnreadMessageBox(MessageBox):
    @property
    def _messages(self):
        return Message.objects(recipient=self.owner, readed=None)

class DraftsMessageBox(MessageBox):
    pass

class TrashMessageBox(MessageBox):
    pass

class FromUserMessageBox(MessageBox):
    pass

class ToUserMessageBox(MessageBox):
    pass


class MessageBoxFactory(object):
    def __init__(self, owner):
        self.owner = owner

    def __getattribute__(self, item):
        if item == 'sent':
            return SentMessageBox(self.owner)
        elif item == 'incoming':
            return IncomingMessageBox(self.owner)
        elif item == 'unread':
            return UnreadMessageBox(self.owner)

        return super(MessageBoxFactory, self).__getattribute__(item)

class Message(Document):
    TASK_NAME_STORE_READED = 'MESSAGE_STORE_READED'

    sender = ReferenceField('Account')
    recipient = ReferenceField('Account')
    text = StringField(required=True)

    timestamp = DateTimeField()

    readed = DateTimeField()

    sender_deleted = DateTimeField()
    recipient_deleted = DateTimeField()

    meta = {
        'indexes': [
                '-timestamp',
                'sender',
                'recipient',
                'sender_deleted',
                'recipient_deleted',
        ]
    }

    def set_readed(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        self.readed = timestamp
        if settings.TASKS_ENABLED.get(self.TASK_NAME_STORE_READED):
            message_store_set_readed.apply_async(args=[ self.id, timestamp, ])
        else:
            self.save()


    def store_set_readed(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        self.readed = timestamp
        self.save()


    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()


    def delete_from(self, user):
        from apps.social.documents import Account

        if user in self.userlist:
            place = 'msg_sent' if user == self.sender else 'msg_inbox'
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

    @classmethod
    def send(cls, sender, recipient, text):
        msg = Message(sender=sender, recipient=recipient, text=text)
        msg.save()
        return msg
        