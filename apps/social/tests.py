# -*- coding: utf-8 -*-

import unittest

from django.test.client import Client

from apps.social.documents import User

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        User.objects.delete()

        self.c = Client()

        self.acc1 = User.create_user(username='test1', password='123')
        self.acc2 = User.create_user(username='test2', password='123')

        self.c.login(username='test1', password='123')

    def tearDown(self):
        User.objects.delete()

