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
    data_dict = dict(
        form_name='register',
        first_name=u'Юрий\'`-',
        last_name=u'Иванов\'`-',
        email='test@test.com',
        phone_0='905',
        phone_1='3332244',
        password1='1234',
        password2='1234',
    )

    def setUp(self):
        self.tearDown()
        self.c = Client()

    def tearDown(self):
        User.objects.delete()

    def test_valid(self):
        email = RegisterTestCase.data_dict['email']
        response = self.c.post('/', RegisterTestCase.data_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects(email=email).count(), 1)

    def test_unique_email(self):
        email = RegisterTestCase.data_dict['email']
        self.c.post('/', RegisterTestCase.data_dict)
        response = self.c.post('/', RegisterTestCase.data_dict)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects(email=email).count(), 1)

    def test_first_name(self):
        email = RegisterTestCase.data_dict['email']
        data_dict = RegisterTestCase.data_dict.copy()

        for tpl in ['','      ','12345', u'Ять']:
            data_dict['first_name'] = tpl
            response = self.c.post('/', data_dict)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects(email=email).count(), 0)

    def test_last_name(self):
        email = RegisterTestCase.data_dict['email']
        data_dict = RegisterTestCase.data_dict.copy()

        for tpl in ['','      ','12345', u'Ять']:
            data_dict['last_name'] = tpl
            response = self.c.post('/', data_dict)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects(email=email).count(), 0)

    def test_last_name(self):
        email = RegisterTestCase.data_dict['email']
        data_dict = RegisterTestCase.data_dict.copy()

        for tpl in ['','      ','12345', u'Ять']:
            data_dict['last_name'] = tpl
            response = self.c.post('/', data_dict)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects(email=email).count(), 0)

    def test_phone(self):
        email = RegisterTestCase.data_dict['email']
        data_dict = RegisterTestCase.data_dict.copy()

        for tpl1,tpl2 in [
                ('1234','1234567'),
                ('1-23','123-4567'),
                ('1 23','123 4567'),
                ('qwe','qwertyu'),
                ('12','123456'),
                ('','1234567'),
                ('123',''),
                ]:
            data_dict['phone_0'] = tpl1
            data_dict['phone_1'] = tpl2
            response = self.c.post('/', data_dict)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.objects(email=email).count(), 0)