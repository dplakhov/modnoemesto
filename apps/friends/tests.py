# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime as dt

from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.social.documents import User
from .documents import FriendshipOffer, UserFriends



class BasicTestCase(unittest.TestCase):
    def cleanUp(self):
        User.objects.delete()
        UserFriends.objects.delete()
        FriendshipOffer.objects.delete()

    def setUp(self):
        self.cleanUp()

        self.client = Client()

        self.user1 = User.create_user(username='test1', password='123')
        self.user2 = User.create_user(username='test2', password='123')

        self.client.login(username='test1', password='123')

    def tearDown(self):
        self.cleanUp()

class FriendshipTestCase(BasicTestCase):
    def test_friends_empty(self):
        user1 = self.user1
        user2 = self.user2
        friends = user1.friends
        self.failUnless(isinstance(friends, UserFriends))
        self.failUnlessEqual(0, friends.count)
        self.failUnless(friends.can_add(user2) is True)

    def test_send_offer(self):
        user1 = self.user1
        user2 = self.user2
        friends = user1.friends
        OFFER_MESSAGE = 'do it now!!'
        friends.offer_send(user2, OFFER_MESSAGE)
        offer = FriendshipOffer.objects.get(author=user1, recipient=user2)
        self.failUnlessEqual(OFFER_MESSAGE, offer.message)





'''
class FriendshipTestCase(BasicTestCase):

    def setUp(self):
        FriendshipOffer.objects.delete()
        super(FriendshipTestCase, self).setUp()
        self.resp = self.c.get(reverse('social:friend',
                                       kwargs={ 'user_id': self.acc2.id }))

    def tearDown(self):
        FriendshipOffer.objects.delete()
        super(FriendshipTestCase, self).tearDown()

    def test_friendship_offer_creates(self):
        self.assertEquals(self.resp.status_code, 302) # redirect
        self.assertEquals(
            FriendshipOffer.objects(author=self.acc1, recipient=self.acc2).count(), 1)

    def test_friendship_offer_creates_once(self):
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc2.id }))
        self.assertEquals(
            FriendshipOffer.objects(author=self.acc1, recipient=self.acc2).count(), 1)

    def test_friendship_offer_increases_fs_offers_inbox_count(self):
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc2.id }))
        self.acc2.reload()
        self.assertEquals(self.acc2.fs_offers_inbox_count, 1)

    def test_friendship_offer_accepts_successfully(self):
        self.c.login(username=self.acc2.username, password='123')
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc1.id }))
        self.acc1.reload(), self.acc2.reload()
        self.assertTrue(self.acc2 in self.acc1.mutual_friends)
        self.assertTrue(self.acc1 in self.acc2.mutual_friends)
        self.assertEquals(FriendshipOffer.objects.count(), 0)

    def test_accepting_friendship_offer_decreases_fs_offers_inbox_count(self):
        self.c.login(username=self.acc2.username, password='123')
        self.c.get(reverse('social:friend', kwargs={ 'user_id': self.acc1.id }))
        self.acc2.reload()
        self.assertEquals(self.acc2.fs_offers_inbox_count, 0)

    def test_friendship_offer_cancels_successfully(self):
        fso = FriendshipOffer.objects.get()
        self.c.get(reverse('social:cancel_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.assertEquals(FriendshipOffer.objects.count(), 0)

    def test_friendship_offer_cancelling_decreases_fs_offers_inbox_count(self):
        fso = FriendshipOffer.objects.get()
        self.c.get(reverse('social:cancel_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.acc2.reload()
        self.assertEquals(self.acc2.fs_offers_inbox_count, 0)

    def test_friendship_offer_declines_successfully(self):
        self.c.login(username=self.acc2.username, password='123')
        fso = FriendshipOffer.objects.get()
        self.c.get(reverse('social:decline_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.assertEquals(FriendshipOffer.objects.count(), 0)

    def test_friendship_offer_declining_decreases_fs_offers_inbox_count(self):
        self.c.login(username=self.acc2.username, password='123')
        fso = FriendshipOffer.objects.get()
        self.c.get(reverse('social:decline_fs_offer',
                           kwargs={ 'offer_id': fso.id }))
        self.assertEquals(self.acc2.fs_offers_inbox_count, 0)



class MassFriendshipTestCase(BasicTestCase):

    def setUp(self):
        FriendshipOffer.objects.delete()
        super(MassFriendshipTestCase, self).setUp()

    def tearDown(self):
        FriendshipOffer.objects.delete()
        super(MassFriendshipTestCase, self).tearDown()

    def test_mass_friendship_limits(self):
        FriendshipOffer.objects.delete()
        c2 = Client()
        print
        for i in xrange(501):
            if not i % 25:
                print  '\rmass friending.. %002d%%' % (i*100/500),
                sys.stdout.flush()
            acc = User.create_user(username='masstest%s' % i,
                                      password='123')
            c2.login(username='masstest%s' % i, password='123')
            acc.save()
            self.c.get(reverse('social:friend', kwargs={ 'user_id': acc.id }))
            c2.get(reverse('social:friend', kwargs={ 'user_id': self.acc1.id }))

        # one last offer violates limits, so it's not accepted
        self.assertEquals(FriendshipOffer.objects.count(), 1)

        self.acc1.reload()

        # no more than 500 mutual friends
        self.assertEquals(len(self.acc1.mutual_friends), 500)
'''
