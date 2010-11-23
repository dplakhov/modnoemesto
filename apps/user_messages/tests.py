# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime as dt

from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.utils.test import patch_settings

from apps.social.documents import Account
from .documents import Message, IncomingMessageBox, SentMessageBox
from apps.user_messages.documents import UnreadMessageBox
from time import sleep

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        Account.objects.delete()
        Message.objects.delete()

        self.c = Client()

        self.acc1 = Account.create_user(username='test1', password='123')
        self.acc2 = Account.create_user(username='test2', password='123')

        self.c.login(username='test1', password='123')

    def tearDown(self):
        Account.objects.delete()
        Message.objects.delete()

class MessageTestCase(BasicTestCase):
    def test_message_box(self):
        user = self.acc1
        self.failUnless(isinstance(user.messages.sent, SentMessageBox))
        self.failUnless(isinstance(user.messages.incoming, IncomingMessageBox))
        self.failUnless(isinstance(user.messages.unread, UnreadMessageBox))
        self.failUnlessEqual(0, len(user.messages.sent))
        self.failUnlessEqual(0, len(user.messages.incoming))
        self.failUnlessEqual(0, len(user.messages.unread))

    def test_message_send(self):
        user1, user2 = self.acc1, self.acc2
        text = 'zzZZzz'
        msg = Message.send(sender=user1, recipient=user2, text=text)

        self.failUnless(msg in user1.messages.sent)
        self.failIf(msg in user2.messages.sent)

        self.failIf(msg in user1.messages.incoming)
        self.failUnless(msg in user2.messages.incoming)

        self.failIf(msg in user1.messages.unread)
        self.failUnless(msg in user2.messages.unread)

    def test_message_read(self):
        user1, user2 = self.acc1, self.acc2
        text = 'zzZZzz'
        msg = Message.send(sender=user1, recipient=user2, text=text)

        with patch_settings(TASKS_ENABLED={}):
            msg.set_readed()

        self.failUnless(msg in user2.messages.incoming)
        self.failIf(msg in user2.messages.unread)

    def test_message_store_read_task(self):
        user1, user2 = self.acc1, self.acc2
        text = 'zzZZzz'
        msg = Message.send(sender=user1, recipient=user2, text=text)

        with patch_settings(TASKS_ENABLED={Message.TASK_NAME_STORE_READED: True}):
            msg.set_readed()
            sleep(1)

            self.failUnless(msg in user2.messages.incoming)
            self.failIf(msg in user2.messages.unread)


class SingleMessageTestCase(BasicTestCase):

    text = 'test text'

    def setUp(self):
        super(SingleMessageTestCase, self).setUp()
        self.resp = self.c.post(
            reverse('user_messages:send_message', kwargs={ 'user_id': self.acc2.id }),
            { 'text': self.text }
        )

        self.msg = Message.objects.get()
        self.acc1.reload()
        self.acc2.reload()

    def test_send_one_message_succeeds(self):
        self.assertEquals(self.resp.status_code, 302) # redirect

    def test_message_adds_to_sender_sent(self):
        self.assertTrue(
            Account.objects(username=self.acc1.username,
                            msg_sent=self.msg).count()
        )

    def test_message_adds_to_rcpt_inbox(self):
        self.assertTrue(
            Account.objects(username=self.acc2.username,
                            msg_inbox=self.msg).count()
        )

    def test_message_is_unread_by_default(self):
        self.assertFalse(self.acc2.msg_inbox[0].is_read)

    def test_recipient_unread_msg_count_increased(self):
        self.assertEquals(self.acc2.unread_msg_count, 1)

    def test_viewed_incoming_message_marks_as_read(self):
        self.c.login(username='test2', password='123')
        resp = self.c.get(
            reverse('user_messages:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.msg.reload()
        self.assertTrue(self.msg.is_read)

    def test_viewed_incoming_message_decreases_unread_msg_count(self):
        self.c.login(username='test2', password='123')
        resp = self.c.get(
            reverse('user_messages:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.acc2.reload()
        self.assertEquals(self.acc2.unread_msg_count, 0)

    def test_viewed_sent_message_remains_unread(self):
        resp = self.c.get(
            reverse('user_messages:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.msg.reload()
        self.assertFalse(self.msg.is_read)


class MassMessagingTestCase(BasicTestCase):
    MAX_MESSAGES_COUNT = 10

    text = 'test text'


    def run(self, *args, **kwargs):
        with patch_settings(MAX_USER_MESSAGES_COUNT=self.MAX_MESSAGES_COUNT):
            result = super(MassMessagingTestCase, self).run(*args, **kwargs)
        return result

    def setUp(self):
        super(MassMessagingTestCase, self).setUp()
        from django.conf import settings
        print
        for i in range(1, settings.MAX_USER_MESSAGES_COUNT + 1):
            if not i % settings.MAX_USER_MESSAGES_COUNT / 50:
                print  '\rmass messaging.. %002d%%' % (i*100/settings.MAX_USER_MESSAGES_COUNT),
                sys.stdout.flush()
            self.resp = self.c.post(
                reverse('user_messages:send_message', kwargs={
                    'user_id': self.acc2.id }),
                { 'text': '%s %s' % (self.text, i) }
            )
        print '\ndone.'
        self.acc1.reload()
        self.acc2.reload()

    def test_only_n_messages_exists(self):
        self.assertEquals(self.MAX_MESSAGES_COUNT, Message.objects.count())

    def test_message_inbox_queue_correct_shifting(self):
        # assert first (with #0) message is gone
        self.assertEquals(self.acc2.msg_inbox[0].text, '%s %s' % (self.text, 1))

    def test_message_sent_queue_correct_shifting(self):
        # assert first (with #0) message is gone
        self.assertEquals(self.acc1.msg_sent[0].text, '%s %s' % (self.text, 1))

