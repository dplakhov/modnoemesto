import uuid

from datetime import timedelta, datetime
from collections import deque
import random

from django.test import TestCase
from django.core.cache import cache

from apps.social.documents import User
from apps.chat.models import Chat, ChatStorage, Message
from django.conf import settings

USERS_COUNT = 10

class ChatTest(TestCase):
    def setUp(self):
        self.cleanUp()

        self.chat = Chat(str(uuid.uuid1()))
        self.online_users = []

        self.setup_users()
        self.setup_offline_users()
        self.setup_current_user_online()

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        User.objects.all().delete()

    def setup_current_user_online(self):
        self.current_user.set_online()

    def setup_users(self):
        self.test_user = User.create_user(email='test@web-mark.ru', password='123')
        self.current_user = User.create_user(email='eugene@web-mark.ru', password='123')
        self.online_users.append(self.current_user)
        self.online_users.append(self.test_user)

        for i in range(USERS_COUNT):
            user = User.create_user(email='user%d@web-mark.ru' % i, password='123')
            user.save()
            self.online_users.append(user)

    def setup_online_users(self):
        for user in self.online_users:
            user.last_access = datetime.now()
            user.save()

    def setup_offline_users(self):
        for user in self.online_users:
            user.last_access = datetime.now() - timedelta(minutes=30)
            user.save()

    def _test_users_online(self):
        chat = self.chat
        storage = ChatStorage(chat.id)

        user_id = self.current_user.pk
        self.failUnlessEqual(0, len(storage.online_users()))
        storage.set_user_online(user_id)
        self.failUnlessEqual(1, len(storage.online_users()))

        user_id = random.randint(0, 100)
        storage.set_user_online(user_id)
        self.failUnlessEqual(2, len(storage.online_users()))

        storage.set_user_offline(user_id)
        self.failUnlessEqual(1, len(storage.online_users()))


    def test_empty_chat(self):
        chat = self.chat
        self.failUnlessEqual([], chat.messages)

    def test_add_message(self):
        chat = self.chat
        user_id = self.test_user.id
        text = "test message"

        message = chat.add_message(user_id=user_id, text=text)
        self.failUnless(isinstance(message, Message))
        self.failUnlessEqual(user_id, message.user_id)
        self.failUnlessEqual(text, message.text)
        #self.failUnlessAlmostEqual(datetime.now(), message.date)


        self.failUnlessEqual([message, ], chat.messages)

    def _test_chat_store(self):
        chat = self.chat
        user_id = self.test_user.id
        text = "test message"

        message = chat.add_message(user_id=user_id, text=text)
        chat = Chat(chat.id)
        self.failUnlessEqual([message, ], chat.messages)

    def test_storage(self):
        chat = self.chat
        storage = ChatStorage(chat.id)
        self.failUnlessEqual([], storage.all())

        user_id = self.test_user.id
        text = "test message"

        message = Message(user_id, text)
        storage.put(message)

        storage = ChatStorage(chat.id)
        self.failUnlessEqual([message], storage.all())

    def test_storage_poinert(self):
        chat = self.chat
        storage = ChatStorage(chat.id)
        user_id = self.test_user.id
        text = "test message %d"
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
        user_id = self.test_user.id
        text = "test message %d"
        messages = deque([], settings.CHAT_MAX_ITEMS)
        for i in range(settings.CHAT_MAX_ITEMS + 7):
            message = Message(user_id, text % i)
            messages.append(message)
            storage.put(message)
        #time.sleep(2)
        storage = ChatStorage(chat.id)
        self.failUnlessEqual(list(messages), storage.all())








