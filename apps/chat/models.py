# -*- encoding: UTF-8 -*-

from datetime import datetime
import time
import hashlib

from django.core.cache import cache
from django.utils.encoding import smart_str

from apps.social.documents import User
from apps.utils.lock import CacheLock

try:
    import json
except:
    import django.utils.simplejson as json


MAX_ITEMS = 3
DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"


class ChatStorage(object):
    def __init__(self, id):
        self.id = id

    def all_json(self):
        data = [ i.get_dict() for i in self.all()]
        return json.dumps(data, ensure_ascii=False)

    def all(self):
        messages_keys = [
            '%s_%d' % (self.id, i) for i in range(MAX_ITEMS)
        ]
        lock_key = hashlib.md5("".join(messages_keys)).hexdigest()
        with CacheLock(lock_key):        
            messages = cache.get_many(messages_keys)
        
        messages = messages.values()         
        messages.sort()
        return messages
    
    def get_by_offset(self, offset):
        last_date = datetime.strptime(offset, DATE_FORMAT)
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
            pointer = pointer % MAX_ITEMS
        
        with CacheLock(pointer_key):
            cache.set(pointer_key, pointer)
        
        message_key = "%s_%d" % (self.id, pointer)
        
        with CacheLock(message_key):
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
    def __init__(self, user_id, text):
        self.user_id = user_id
        self.text = text
        self.date = datetime.now()

    def get_dict(self):
        user = User.objects.get(pk=self.user_id)
        return {
                 'user_id': str(self.user_id),
                 'user_name': user.get_full_name(),
                 'date': self.date.strftime(DATE_FORMAT),
                 'text': self.text,
                }
                
    def __eq__(self, other):
        return (self.user_id == other.user_id
                and  self.text == other.text
                and  self.date == other.date
                )
    def __repr__(self):
        #return "[%s, %s]" % (self.text, self.date.strftime("%Y-%m-%d %H:%M:%S:%f"))
        return "[%s %s]" % (self.text, self.date.strftime(DATE_FORMAT))
    
    def __cmp__(self, other):
        return cmp(self.date, other.date)
