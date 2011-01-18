# -*- coding: utf-8 -*-

import os
from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test.client import Client

from mongoengine.connection import _get_db
import gridfs

from ..documents import *

class ThemeTest(TestCase):
    def setUp(self):
        Theme.objects.delete()
        ThemeFile.objects.delete()

    def _test_theme(self, theme):
        self.failUnless(isinstance(theme, Theme))
        self.failUnless(theme.is_public)
        self.failUnlessEqual(u'Тема', theme.name)
        self.failUnlessEqual(u'Описание', theme.description)

        file = theme.files['style.css']
        self.failUnless(isinstance(file, ThemeFile))

        self.failIfEqual(-1, file.read().find('background-image'))
        self.failUnlessEqual('text/css', file.content_type)


    def test_from_directory(self):
        theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                'files/theme1'))
        self._test_theme(theme)

    def test_from_directory__notexists(self):
        self.failUnlessRaises(Theme.SourceFileNotExists,
                              Theme.from_directory,
                              os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        
    def test_from_zip(self):
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        self._test_theme(theme)

    def test_update_from_zip(self):
        old_theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        new_theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))

        self.failUnlessEqual(old_theme.id, new_theme.id)

    def test_update_from_directory(self):
        old_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                    'files/theme1'))
        new_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                'files/theme1'))

        self.failUnlessEqual(old_theme.id, new_theme.id)

    def test_from_zip__notexists(self):
        self.failUnlessRaises(Theme.SourceFileNotExists, Theme.from_zip,
                              'notexists.zip')

    def test_view(self):
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        client = Client()

        response = client.get(reverse('themes:file_view',
                                      kwargs=dict(theme_id=theme.id,
                                                  file_name='style.css')
                           ))

        self.failUnlessEqual(200, response.status_code)

        self.failIfEqual(-1, response.content.find('background-image'))
        self.assertEquals('text/css', response['Content-Type'])

    def test_view_file_not_found(self):
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        client = Client()
        response = client.get(reverse('themes:file_view',
                                      kwargs=dict(theme_id=theme.id,
                                                  file_name='not_found.css')
                           ))

        self.failUnlessEqual(404, response.status_code)

    def TODO_test_theme_delete(self):
        fs = gridfs.GridFS(_get_db())
        print dir(fs)
        print fs.list()
