# -*- coding: utf-8 -*-
from datetime import datetime
import sys

from django.test import TestCase

from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.social.documents import Account
from .documents import Message

class BasicTestCase(TestCase):

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
        print repr(self.resp)

    def tearDown(self):
        super(SingleMessageTestCase, self).tearDown()

    def test_send_one_message_succeeds(self):
        self.assertEquals(self.resp.status_code, 302) # redirect

    def test_message_adds_to_author_sent(self):
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

    def setUp(self):
        super(MassMessagingTestCase, self).setUp()
        print
        for i in xrange(501):
            if not i % 25:
                print  '\rmass messaging.. %002d%%' % (i*100/500),
                sys.stdout.flush()
            self.resp = self.c.post(
                reverse('user_messages:send_message', kwargs={
                    'user_id': self.acc2.id }),
                { 'text': '%s %s' % (self.text, i) }
            )
        print '\ndone.'
        self.acc1.reload()
        self.acc2.reload()

    def tearDown(self):
        super(MassMessagingTestCase, self).tearDown()

    def test_only_500_messages_exists(self):
        self.assertEquals(Message.objects.count(), 500)

    def test_message_inbox_queue_correct_shifting(self):
        # assert first (with #0) message is gone
        self.assertEquals(self.acc2.msg_inbox[0].text, '%s %s' % (self.text, 1))

    def test_message_sent_queue_correct_shifting(self):
        # assert first (with #0) message is gone
        self.assertEquals(self.acc1.msg_sent[0].text, '%s %s' % (self.text, 1))

