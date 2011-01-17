# -*- coding: utf-8 -*-

import os

from django.test import TestCase

from ..documents import *

class ThemeTest(TestCase):
    def test_from_zip(self):
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                            'files/theme1.zip'))

    def test_from_zip__notexists(self):
        self.failUnlessRaises(Theme.SourceFileNotExists, Theme.from_zip,
                              'notexists.zip')
    def test_view(self):
        theme = Theme()

