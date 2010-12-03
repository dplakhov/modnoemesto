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

    def test_send_offer(self):
        user1 = self.user1
        user2 = self.user2
        friends = user1.friends
        OFFER_MESSAGE1 = u'добавь меня'
        friends.offers.send(user2, OFFER_MESSAGE1)
        offer = FriendshipOffer.objects.get(author=user1, recipient=user2)
        self.failUnlessEqual(OFFER_MESSAGE1, offer.message)

        self.failUnless(friends.can_add(user2) is False)

        OFFER_MESSAGE2 = u'почему не добавляешь-то??'
        friends.offers.send(user2, OFFER_MESSAGE2)
        self.failUnlessEqual(1,
                 FriendshipOffer.objects(author=user1, recipient=user2).count())

        offer = FriendshipOffer.objects.get(author=user1, recipient=user2)
        self.failUnlessEqual(OFFER_MESSAGE1, offer.message)


    def test_accept_offer(self):
        user1 = self.user1
        user2 = self.user2
        user1.friends.offers.send(user2)


