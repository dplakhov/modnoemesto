# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase
from .common import file_path, create_file

class TemplatetagsTest(TestCase):
    def test_media_url(self):
        file = create_file()
        file.apply_transformations()
        url = reverse('media:file_view', kwargs=dict(file_id=file.id,
                                                     transformation_name='thumb.png'))
        print url
        template = '''{% load media %}{% media_url file 'thumb.png' %}'''
        #rendered =