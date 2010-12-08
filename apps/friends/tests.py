# -*- coding: utf-8 -*-
import sys
import unittest
from datetime import datetime as dt

from django.test.client import Client
from django.core.urlresolvers import reverse

from apps.social.documents import User
from .documents import FriendshipOffer, UserFriends, FriendshipOfferList



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
        self.failUnless(isinstance(user1.friends, UserFriends))
        self.failUnlessEqual(0, user1.friends.count)
        self.failUnless(user1.friends.can_add(user2) is True)
        self.failUnless(isinstance(user1.friends.offers, FriendshipOfferList))
        self.failIf(user1.friends.offers.sent)
        self.failIf(user1.friends.offers.incoming)


    def test_send_offer(self):
        user1 = self.user1
        user2 = self.user2

        OFFER_MESSAGE1 = u'добавь меня'
        user1.friends.offers.send(user2, OFFER_MESSAGE1)
        offer = FriendshipOffer.objects.get(sender=user1, recipient=user2)
        self.failUnlessEqual(OFFER_MESSAGE1, offer.message)

        self.failIf(user1.friends.can_add(user2))
        self.failUnless(user2.friends.can_add(user1))

        OFFER_MESSAGE2 = u'почему не добавляешь-то??'
        user1.friends.offers.send(user2, OFFER_MESSAGE2)
        self.failUnlessEqual(1,
                 FriendshipOffer.objects(sender=user1, recipient=user2).count())

        offer = FriendshipOffer.objects.get(sender=user1, recipient=user2)
        self.failUnlessEqual(OFFER_MESSAGE1, offer.message)

        self.failUnlessEqual(1, len(user1.friends.offers.sent))
        self.failUnlessEqual(1, len(user2.friends.offers.incoming))

        self.failIf(user1.friends.offers.incoming)
        self.failIf(user2.friends.offers.sent)

        self.failUnless(user2.friends.offers.has_from_user(user1))

    def test_offer_cancel(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends.offers.send(user2)

        user1.friends.offers.cancel(user2)

        self.failIf(user1.friends.offers.incoming)
        self.failIf(user1.friends.offers.sent)

        self.failIf(user2.friends.offers.incoming)
        self.failIf(user2.friends.offers.sent)

    def test_offer_accept(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends.offers.send(user2)

        user2.friends.offers.accept(user1)

        self.failIf(user1.friends.offers.sent)
        self.failIf(user1.friends.offers.incoming)

        self.failIf(user2.friends.offers.sent)
        self.failIf(user2.friends.offers.incoming)

        user1.reload()
        user2.reload()

        self.failUnless(user1.friends.list)
        self.failUnless(user2 in user1.friends.list)

        self.failUnless(user2.friends.list)
        self.failUnless(user1 in user2.friends.list)

        self.failUnless(user1.friends.contains(user2))
        self.failUnless(user2.friends.contains(user1))

        self.failUnlessEqual(1, user1.friends.count)
        self.failUnlessEqual(1, user2.friends.count)

        self.failIf(user1.friends.can_add(user2))
        self.failIf(user2.friends.can_add(user1))

        self.failIf(user1.friends.can_add(user2))
        self.failIf(user2.friends.can_add(user1))

    def test_offer_reject(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends.offers.send(user2)
        user2.friends.offers.reject(user1)

        user1.reload()
        user2.reload()
        
        self.failIf(user1.friends.list)
        self.failIf(user2 in user1.friends.list)

        self.failIf(user2.friends.list)
        self.failIf(user1 in user2.friends.list)

        self.failIf(user1.friends.contains(user2))
        self.failIf(user2.friends.contains(user1))

        self.failUnlessEqual(0, user1.friends.count)
        self.failUnlessEqual(0, user2.friends.count)


    def test_unfriend(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends.offers.send(user2)
        user2.friends.offers.accept(user1)

        user1.reload()
        user2.reload()

        user1.friends.unfriend(user2)

        user1.reload()
        user2.reload()

        self.failIf(user1.friends.list)
        self.failIf(user2 in user1.friends.list)

        self.failIf(user2.friends.list)
        self.failIf(user1 in user2.friends.list)

        self.failIf(user1.friends.contains(user2))
        self.failIf(user2.friends.contains(user1))

        self.failUnlessEqual(0, user1.friends.count)
        self.failUnlessEqual(0, user2.friends.count)
        

    def test_send_accepts_other_offer(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends.offers.send(user2)
        user2.friends.offers.send(user1)

        self.failIf(user1.friends.offers.sent)
        self.failIf(user1.friends.offers.incoming)

        self.failIf(user2.friends.offers.sent)
        self.failIf(user2.friends.offers.incoming)

        user1.reload()
        user2.reload()

        self.failUnless(user1.friends.contains(user2))
        self.failUnless(user2.friends.contains(user1))

        self.failUnlessEqual(1, user1.friends.count)
        self.failUnlessEqual(1, user2.friends.count)

    def test_friends__add_adds_only_once_friend(self):
        user1 = self.user1
        user2 = self.user2

        user1.friends._add(user2)
        self.failUnless(user1.friends.contains(user2))
        user1.friends._add(user2)

        self.failUnlessEqual(1, user1.friends.count)

        user1.reload()
        self.failUnlessEqual(1, user1.friends.count)