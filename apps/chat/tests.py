import uuid

from datetime import datetime
from collections import deque

from django.test import TestCase
from django.core.cache import cache

from apps.social.documents import User
from apps.chat.models import Chat, ChatStorage, Message, MAX_ITEMS


class ChatTest(TestCase):
    def setUp(self):
        self.chat = Chat(str(uuid.uuid1()))
        User.objects.delete()

        #self.c = Client()

        self.acc1 = User.create_user(email='test1@web-mark.ru', password='123')
        self.acc2 = User.create_user(email='test2@web-mark.ru', password='123')
        
    
    def test_empty_chat(self):
        chat = self.chat
        self.failUnlessEqual([], chat.messages)
        
    def test_add_message(self):
        chat = self.chat
        user_id = self.acc1.id
        text="test message"
        
        message = chat.add_message(user_id=user_id, text=text)
        self.failUnless(isinstance(message, Message))
        self.failUnlessEqual(user_id, message.user_id)
        self.failUnlessEqual(text, message.text)
        #self.failUnlessAlmostEqual(datetime.now(), message.date)
        
        
        self.failUnlessEqual([message,], chat.messages)
        
    def _test_chat_store(self):
        chat = self.chat
        user_id = self.acc1.id
        text="test message"
        
        message = chat.add_message(user_id=user_id, text=text)
        chat = Chat(chat.id)
        self.failUnlessEqual([message,], chat.messages)
        
    def test_storage(self):
        chat = self.chat
        storage = ChatStorage(chat.id)
        self.failUnlessEqual([], storage.all())

        user_id = self.acc1.id
        text="test message"
        
        message = Message(user_id, text)
        storage.put(message)
        
        storage = ChatStorage(chat.id)
        self.failUnlessEqual([message], storage.all())
        
    def test_storage_poinert(self):
        chat = self.chat
        storage = ChatStorage(chat.id)
        user_id = self.acc1.id
        text="test message %d"
        messages = []
        for i in range(2):
            message = Message(user_id, text % i)
            messages.append(message)
            storage.put(message)
        
        storage = ChatStorage(chat.id)
        self.failUnlessEqual(messages, storage.all())
        
    def test_storage_poinert_overflow(self):
        chat = self.chat
        storage = ChatStorage(chat.id)
        user_id = self.acc1.id
        text="test message %d"
        messages = deque([], MAX_ITEMS)
        for i in range(MAX_ITEMS + 7):
            message = Message(user_id, text % i)
            messages.append(message)
            storage.put(message)
        #time.sleep(2)
        storage = ChatStorage(chat.id)
        self.failUnlessEqual(list(messages), storage.all())
        
        
        
        
        
        
        
        
        