# -*- coding: utf-8 -*-

import unittest

from django.test.client import Client

from apps.social.documents import User

class BasicTestCase(unittest.TestCase):

    def setUp(self):
        User.objects.delete()

        self.c = Client()

        self.acc1 = User.create_user(email='test1@web-mark.ru', password='123')
        self.acc2 = User.create_user(email='test2@web-mark.ru', password='123')

        self.c.login(email='test1@web-mark.ru', password='123')

    def tearDown(self):
        User.objects.delete()


class RegisterTestCase(unittest.TestCase):

    def setUp(self):
        self.tearDown()
        self.c = Client()

    def tearDown(self):
        User.objects.delete()

    def test_valid(self):
        email = 'test@test.com'
        response = self.c.post('/', dict(
            form_name='register',
            first_name=u'Юрий',
            last_name=u'Иванов',
            email=email,
            phone_0='905',
            phone_1='3332244',
            password1='1234',
            password2='1234',
        ))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects(email=email).count(), 1)

    def test_unique_email(self):
        email = 'test@test.com'
        data_dict = dict(
            form_name='register',
            first_name=u'Юрий',
            last_name=u'Иванов',
            email=email,
            phone_0='905',
            phone_1='3332244',
            password1='1234',
            password2='1234',
        )
        self.c.post('/', data_dict)
        response = self.c.post('/', data_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects(email=email).count(), 1)