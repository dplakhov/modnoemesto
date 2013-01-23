# -*- coding: utf-8 -*-

import os
from django.core.urlresolvers import reverse
from django.template.context import RequestContext

from django.test import TestCase
from django.test.client import Client
from django.template import loader

from mongoengine.connection import _get_db
import gridfs

from ..documents import *

from ..thread_locals import _thread_locals

TEMPLATE_NAME = 'dir/test_template.html'

class ThemeTest(TestCase):
    def setUp(self):
        Theme.objects.delete()
        ThemeFile.objects.delete()
        ThemeTemplate.objects.delete()

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

    def test_with_html(self):
        theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                    'files/theme2'))
        
        self.failUnlessEqual('<h1>I am superstar</h1>', theme.html_top)

    def test_with_html_replaced(self):
        old_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                    'files/theme2'))

        self.failUnless(old_theme.html_top)

        new_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                'files/theme1'))

        self.failIf(new_theme.html_top)

    def test_old_files_deleted(self):
        old_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                            'files/theme1'))

        self.failUnlessEqual(3, ThemeFile.objects().count())

        new_theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                'files/theme2'))

        self.failUnlessEqual(2, ThemeFile.objects().count())

    def test_with_html_replace_src(self):
        theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                    'files/theme3'))

        self.failUnlessEqual('<img src="/theme/%s/preview.png" />' % theme.id,
                             theme.html_top)


    def _test_template(self, theme):
        self.failUnlessEqual(1, ThemeTemplate.objects().count())

        template = theme.templates[TEMPLATE_NAME]
        self.failUnless(isinstance(template, ThemeTemplate))
        self.failUnlessEqual(TEMPLATE_NAME, template.name)

        setattr(_thread_locals, 'current_theme', theme)
        template = loader.get_template(TEMPLATE_NAME)
        c = RequestContext({})
        rendered = template.render(c)
        self.failIfEqual(-1, rendered.find(u'<title>Привет, template</title>'))


    def test_template_from_directory(self):
        self.failIf(ThemeTemplate.objects().count())
        theme = Theme.from_directory(os.path.join(os.path.dirname(__file__),
                                                    'files/theme4'))

        self._test_template(theme)


    def test_template_from_zip(self):
        self.failIf(ThemeTemplate.objects().count())
        theme = Theme.from_zip(os.path.join(os.path.dirname(__file__),
                                                    'files/theme4.zip'))

        self._test_template(theme)
