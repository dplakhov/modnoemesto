# -*- coding: utf-8 -*-
import unittest
from django.test.client import Client
from apps.social.documents import User
from apps.groups.documents import Group, GroupUser
from django.core.urlresolvers import reverse


class GroupTest(unittest.TestCase):

    group_fields = {
        'name':'',
        'public': '',
        'description':'',
        'theme':'',
        'type':'',
        'site':'',
        'country':'',
        'city':'',
    }

    def setUp(self):
        self.tearDown()
        self.c = Client()
        self.user_group_admin = User.create_user(username='group_admin', password='123')
        self.user_other = User.create_user(username='other', password='123')
        self.user_superuser = User.create_user(username='superuser', password='123', is_superuser=True)

    def tearDown(self):
        GroupUser.objects.delete()
        Group.objects.delete()
        User.objects.delete()

    def _group_create(self, **kwarg):
        data = GroupTest.group_fields.copy()
        data.update(kwarg)
        return self.c.post(reverse('groups:group_add'), data=data)

    def _get_group_id(self, response):
        return response.get('Location', '').rstrip('/').split('/')[-1]

    def test_group_create(self):
        self.c.login(username='group_admin', password='123')

        response = self._group_create(name='Group',
                                      public='true')
        self.assertEqual(response.status_code, 302)
        group_id = self._get_group_id(response)
        self.assertEqual(Group.objects(id=group_id).count(), 1)

    def test_free_group_view(self):
        self.c.login(username='group_admin', password='123')
        response = self._group_create(name='Group Free',
                                      public='true')
        group_id = self._get_group_id(response)

        self.c.login(username='group_admin', password='123')
        response = self.c.get(reverse('groups:group_view', args=[group_id]))
        self.assertEqual(response.status_code, 200)

        self.c.login(username='other', password='123')
        response = self.c.get(reverse('groups:group_view', args=[group_id]))
        self.assertEqual(response.status_code, 200)

        self.c.login(username='superuser', password='123')
        response = self.c.get(reverse('groups:group_view', args=[group_id]))
        self.assertEqual(response.status_code, 200)

    def test_free_group_edit(self):
        self.c.login(username='group_admin', password='123')
        response = self._group_create(name='Group Free',
                                      public='true')
        group_id = self._get_group_id(response)

        self.c.login(username='group_admin', password='123')
        response = self.c.get(reverse('groups:group_edit', args=[group_id]))
        self.assertEqual(response.status_code, 200)

        self.c.login(username='other', password='123')
        response = self.c.get(reverse('groups:group_edit', args=[group_id]))
        self.assertEqual(response.status_code, 302)

        self.c.login(username='superuser', password='123')
        response = self.c.get(reverse('groups:group_edit', args=[group_id]))
        self.assertEqual(response.status_code, 200)
