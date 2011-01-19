# -*- encoding: UTF-8 -*-

from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils.encoding import smart_str
from django.conf import settings

from apps.social.documents import User
from apps.utils.lock import CacheLock

try:
    import json
except:
    import django.utils.simplejson as json


class ChatStorage(object):
    def __init__(self, id):
        self.id = id
        self.users_key = '%s_ou' % (self.id,)

    def set_user_offline(self, user_id):
        users = self.online_users()
        users[user_id] = datetime.now() - timedelta(seconds=settings.CHAT_OFFLINE_TIMEDELTA)
        cache.set(self.users_key, users)

    def set_user_online(self, user_id):
        users = self.online_users()
        users[user_id] = datetime.now()
        cache.set(self.users_key, users)

    def cleanup_users(self):
        users = cache.get(self.users_key) or {}
        now_offset = datetime.now() - timedelta(seconds=settings.CHAT_OFFLINE_TIMEDELTA)

        for pk in users.keys():
            last_access = users[pk]
            if last_access < now_offset:
                del users[pk]
                user = User.objects.get(pk=pk)
                system_message = Message(
                    pk,
                    u'%s выходит из чата.' % user.get_full_name(),
                    type=Message.TYPE_SYSTEM
                )
                self.put(system_message)



        cache.set(self.users_key, users)

    def online_users(self):
        self.cleanup_users()
        users = cache.get(self.users_key)

        if not users:
            users = {}
            cache.set(self.users_key, users)

        return users

    def all_json(self):
        data = [ i.get_dict() for i in self.all()]
        return json.dumps(data, ensure_ascii=False)

    def all(self):
        messages_keys = [
            '%s_%d' % (self.id, i) for i in range(settings.CHAT_MAX_ITEMS)
        ]

        messages = cache.get_many(messages_keys)

        messages = messages.values()
        messages.sort()
        return messages

    def get_by_offset(self, offset):
        last_date = datetime.strptime(offset, settings.CHAT_MESSAGE_DATE_FORMAT)
        last_messages = [message for message in self.all() if message.date > last_date]
        return last_messages

    def get_by_offset_json(self, offset):
        data = [ i.get_dict() for i in self.get_by_offset(offset)]
        return json.dumps(data, ensure_ascii=False)

    def put(self, message):
        pointer_key = '%s_p' % (self.id,)
        with CacheLock(pointer_key):
            pointer = cache.get(pointer_key)

            if pointer is None:
                pointer = 0
            else:
                pointer += 1
                pointer = pointer % settings.CHAT_MAX_ITEMS

            cache.set(pointer_key, pointer)

            message_key = "%s_%d" % (self.id, pointer)


            cache.set(message_key, message)

class Chat(object):
    def __init__(self, id):
        self.id = id
        self._messages = []

    @property
    def messages(self):
        return self._messages

    def add_message(self, user_id, text):
        message = Message(user_id, text)
        self._messages.append(message)
        return message



class Message(object):
    TYPE_USER = 'user'
    TYPE_SYSTEM = 'system'

    def __init__(self, user_id, text, type=TYPE_USER):
        self.user_id = user_id
        self.text = text
        self.date = datetime.now()
        self.type = type

    def get_dict(self):
        user = User.objects.get(pk=self.user_id)
        return {
                 'user_id': str(self.user_id),
                 'user_name': user.get_full_name(),
                 'date': self.date.strftime(settings.CHAT_MESSAGE_DATE_FORMAT),
                 'text': self.text,
                 'type': self.type,
                }

    def __eq__(self, other):
        return (self.user_id == other.user_id
                and  self.text == other.text
                and  self.date == other.date
                )
    def __repr__(self):
        #return "[%s, %s]" % (self.text, self.date.strftime("%Y-%m-%d %H:%M:%S:%f"))
        return "[%s %s %s]" % (self.text, self.date.strftime(settings.CHAT_MESSAGE_DATE_FORMAT), self.type)

    def __cmp__(self, other):
        return cmp(self.date, other.date)
