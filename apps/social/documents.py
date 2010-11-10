from datetime import datetime
from mongoengine import *
from mongoengine import connection

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from auth import User


class LimitsViolationException(Exception):
    def __init__(self, cause):
        self.cause = cause
        super(LimitsViolationException, self).__init__()


class Account(User):
    groups = ListField(ReferenceField('Group'))

    # subscriptions
    mutual_friends = ListField(ReferenceField('Account'))

    # messaging
    msg_inbox = ListField(ReferenceField('Message'))
    msg_sent = ListField(ReferenceField('Message'))

    # some denormalisation
    friends_count = IntField(default=0)
    unread_msg_count = IntField(default=0)
    msg_inbox_count = IntField(default=0)
    msg_sent_count = IntField(default=0)

    # some control
    version = IntField(default=0)

    def friend(self, user):
        #@todo: maybe move whole routine to some asynchronous worker such as
        # celery
        if FriendshipOffer.objects(recipient=self, author=user).count():
            #@warning: this code is non-transactional
            # minor limits violation is possible due to requests concurrency

            acc1, acc2 = Account.objects(id__in=(self.id, user.id)).only(
                'version', 'friends_count')

            for acc in (acc1, acc2):
                if acc.friends_count > 499:
                    raise LimitsViolationException(acc)

            FriendshipOffer.objects(recipient=self, author=user).delete()

            Account.objects(id=user.id).update_one\
                    (add_to_set__mutual_friends=self, inc__friends_count=1,
                     inc__version=1)
            Account.objects(id=self.id).update_one\
                    (add_to_set__mutual_friends=user, inc__friends_count=1,
                     inc__version=1)
        else:
            FriendshipOffer.objects.get_or_create(recipient=user, author=self)



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



    def send_message(self, text, recipient):
        #@todo: maybe move whole routine to some asynchronous worker such as
        # celery
        import pymongo
        db = connection._get_db()

        msg = Message(text=text, author=self, recipient=recipient,
                      userlist=(self, recipient))
        msg.save()

        # some black magic code template
        code_template = """
            function() {
                var ret = db.user.findOne({ _id: ObjectId('%(user_id)s') },
                { version: 1, msg_%(place)s_count: 1,
                    msg_%(place)s: { $slice: 1 } });

                return ret;
            }
            """

        # we're going to update the document with known version just to ensure
        # that number of msgs never goes out of declared limits (smth about 500)

        code = code_template % { 'user_id': self.id, 'place': 'sent' }
        ret = 0 # ret is a number of the updated documents
        while not ret:
            # reload only version, msg_sent_count and the eldest sent message

            r = db.eval(pymongo.code.Code(code))
            version, msg_sent_count = r['version'], r['msg_sent_count']
            eldest_msg = r['msg_sent'] and Message._from_son(db.dereference\
                    (r['msg_sent'][0])) or None

            if msg_sent_count > 499:
                eldest_msg.delete_from(self)
            else:
                ret = Account.objects(id=self.id, version=version
                    ).update_one(push__msg_sent=msg, inc__msg_sent_count=1,
                             inc__version=1)

        code = code_template % { 'user_id': recipient.id, 'place': 'inbox' }
        ret = 0 # do it again for recipient
        while not ret:
            # reload only version, msg_inbox_count and the eldest received
            # message

            r = db.eval(pymongo.code.Code(code))
            version, msg_inbox_count = r['version'], r['msg_inbox_count'],
            eldest_msg = r['msg_inbox'] and Message._from_son(db.dereference \
                    (r['msg_inbox'][0])) or None

            if msg_inbox_count > 499:
                eldest_msg.delete_from(recipient)
            else:
                ret = Account.objects(id=recipient.id, version=version
                    ).update_one(push__msg_inbox=msg, inc__msg_inbox_count=1,
                         inc__unread_msg_count=1, inc__version=1)


class Group(Document):
    name = StringField(required=True, unique=True)
    members = ListField(ReferenceField('Account'))


class FriendshipOffer(Document):
    timestamp = DateTimeField()
    author = ReferenceField('Account')
    recipient = ReferenceField('Account')

    def __init__(self, *args, **kwargs):
        super(FriendshipOffer, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()


class Message(Document):
    text = StringField(required=True)
    author = ReferenceField('Account')
    recipient = ReferenceField('Account')
    timestamp = DateTimeField()
    userlist = ListField(ReferenceField('Account'))
    is_read = BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()


    def delete_from(self, user):
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
