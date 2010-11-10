import sys
import unittest
from datetime import datetime as dt

from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.social.documents import Account, Message, FriendshipOffer as FSOffer


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


class SingleMessageTestCase(BasicTestCase):

    text = 'test text'

    def setUp(self):
        super(SingleMessageTestCase, self).setUp()
        self.resp = self.c.post(
            reverse('social:send_message', kwargs={ 'user_id': self.acc2.id }),
            { 'text': self.text }
        )
        self.msg = Message.objects.get()
        self.acc1.reload()
        self.acc2.reload()

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
            reverse('social:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.msg.reload()
        self.assertTrue(self.msg.is_read)

    def test_viewed_incoming_message_decreases_unread_msg_count(self):
        self.c.login(username='test2', password='123')
        resp = self.c.get(
            reverse('social:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.acc2.reload()
        self.assertEquals(self.acc2.unread_msg_count, 0)

    def test_viewed_sent_message_remains_unread(self):
        resp = self.c.get(
            reverse('social:view_message', kwargs={
                'message_id': self.acc2.msg_inbox[0].id })
        )
        self.msg.reload()
        self.assertFalse(self.msg.is_read)


class MassMessagingTestCase(BasicTestCase):

    text = 'test text'

    def setUp(self):
        super(MassMessagingTestCase, self).setUp()
        print
        for i in xrange(501):
            if not i % 25:
                print  '\rmass messaging.. %002d%%' % (i*100/500),
                sys.stdout.flush()
            self.resp = self.c.post(
                reverse('social:send_message', kwargs={
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


class FriendshipTestCase(BasicTestCase):

    def setUp(self):
        FSOffer.objects.delete()
        super(FriendshipTestCase, self).setUp()
        self.resp = self.c.get(reverse('social:friend',
                                       kwargs={ 'user_id': self.acc2.id }))

    def tearDown(self):
        FSOffer.objects.delete()
        super(FriendshipTestCase, self).tearDown()

    def test_friendship_offer_creates(self):
        self.assertEquals(self.resp.status_code, 302) # redirect
        self.assertEquals(
            FSOffer.objects(author=self.acc1, recipient=self.acc2).count(), 1)

    def test_friendship_offer_creates_once(self):
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc2.id }))
        self.assertEquals(
            FSOffer.objects(author=self.acc1, recipient=self.acc2).count(), 1)

    def test_friendship_offer_accepts_successfully(self):
        self.c.login(username=self.acc2.username, password='123')
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc1.id }))
        self.acc1.reload(), self.acc2.reload()
        self.assertTrue(self.acc2 in self.acc1.mutual_friends)
        self.assertTrue(self.acc1 in self.acc2.mutual_friends)
        self.assertEquals(FSOffer.objects.count(), 0)

    def test_friendship_offer_cancels_successfully(self):
        fso = FSOffer.objects.get()
        self.c.get(reverse('social:cancel_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.assertEquals(FSOffer.objects.count(), 0)

    def test_friendship_offer_declines_successfully(self):
        self.c.login(username=self.acc2.username, password='123')
        fso = FSOffer.objects.get()
        self.c.get(reverse('social:decline_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.assertEquals(FSOffer.objects.count(), 0)


class MassFriendshipTestCase(BasicTestCase):

    def setUp(self):
        FSOffer.objects.delete()
        super(MassFriendshipTestCase, self).setUp()

    def tearDown(self):
        FSOffer.objects.delete()
        super(MassFriendshipTestCase, self).tearDown()

    def test_mass_friendship_limits(self):
        FSOffer.objects.delete()
        c2 = Client()
        print
        for i in xrange(501):
            if not i % 25:
                print  '\rmass friending.. %002d%%' % (i*100/500),
                sys.stdout.flush()
            acc = Account.create_user(username='masstest%s' % i,
                                      password='123')
            c2.login(username='masstest%s' % i, password='123')
            acc.save()
            self.c.get(reverse('social:friend', kwargs={ 'user_id': acc.id }))
            c2.get(reverse('social:friend', kwargs={ 'user_id': self.acc1.id }))

        # one last offer violates limits, so it's not accepted
        self.assertEquals(FSOffer.objects.count(), 1)

        self.acc1.reload()

        # no more than 500 mutual friends
        self.assertEquals(len(self.acc1.mutual_friends), 500)
