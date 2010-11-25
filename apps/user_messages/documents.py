# -*- coding: utf-8 -*-
from datetime import datetime
from mongoengine import *
from django.conf import settings

from .tasks import (message_store_set_readed, message_store_sender_delete,
    message_store_recipient_delete)

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
        return Message.objects(recipient=self.owner,
                               recipient_delete=None)

class SentMessageBox(MessageBox):
    @property
    def _messages(self):
        return Message.objects(sender=self.owner, 
                               sender_delete=None)

class UnreadMessageBox(MessageBox):
    @property
    def _messages(self):
        return Message.objects(recipient=self.owner,
                               readed=None,
                               recipient_delete=None
                               )

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
    TASK_NAME_DELETE = 'MESSAGE_DELETE'

    sender = ReferenceField('User')
    recipient = ReferenceField('User')
    text = StringField(required=True)

    timestamp = DateTimeField()

    readed = DateTimeField()

    sender_delete = DateTimeField()
    recipient_delete = DateTimeField()

    meta = {
        'indexes': [
                'timestamp',
                'sender',
                'recipient',
                'sender_delete',
                'recipient_delete',
        ],

        'ordering': [
                'timestamp',
        ]

    }

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()

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

    @property
    def is_read(self):
        return bool(self.readed)

    def is_sender(self, user):
        return self.sender.id == user.id

    def is_recipient(self, user):
        return self.recipient.id == user.id

    def set_user_delete(self, user, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        async = settings.TASKS_ENABLED.get(self.TASK_NAME_DELETE)
        if async:
            args = [ self.id, timestamp, ]

        if self.is_sender(user):
            self.sender_delete = timestamp
            if async:
                message_store_sender_delete.apply_async(args=args)
            else:
                self.store_sender_delete(timestamp)
        elif self.is_recipient(user):
            self.recipient_delete = timestamp
            if async:
                message_store_recipient_delete.apply_async(args=args)
            else:
                self.store_recipient_delete(timestamp)
        else:
            raise RuntimeError()

    def store_sender_delete(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        Message.objects(id=self.id).update_one(set__sender_delete=timestamp)

    def store_recipient_delete(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()

        Message.objects(id=self.id).update_one(set__recipient_delete=timestamp)


    def delete(self):
        raise RuntimeError('Can not delete directly')

    def hard_delete(self, safe=False):
        super(Message, self).delete(safe)

    @classmethod
    def send(cls, sender, recipient, text):
        msg = Message(sender=sender, recipient=recipient, text=text)
        msg.save()
        return msg

