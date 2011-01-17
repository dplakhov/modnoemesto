# -*- coding: utf-8 -*-

import os

from django.test import TestCase

from ..documents import *

class ThemeTest(TestCase):
    def setUp(self):
        Theme.objects.delete()

    def test_from_directory(self):
        theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                'files/theme1'))
        self.failUnless(isinstance(theme, Theme))
        self.failUnless(theme.is_public)
        self.failUnlessEqual(u'Тема', theme.name)
        self.failUnlessEqual(u'Описание', theme.description)

    def test_from_directory__notexists(self):
        self.failUnlessRaises(Theme.SourceFileNotExists,
                              Theme.from_directory,
                              os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        
    def test_from_zip(self):
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))
        
        self.failUnless(isinstance(theme, Theme))

    def test_from_zip__notexists(self):
        self.failUnlessRaises(Theme.SourceFileNotExists, Theme.from_zip,
                              'notexists.zip')
    def test_view(self):
        theme = Theme()

