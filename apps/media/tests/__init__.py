# -*- coding: utf-8 -*-

import os
import urllib

from django.test import TestCase

from ..models import *


def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))


class MediaFileTest(TestCase):
    def test_save_empty_file_raises(self):
        file = MediaFile()
        self.failUnlessRaises(File.SourceFileEmpty, file.save)

    def test_save_content_type_unspecified_raises(self):
        file = MediaFile()
        file.file.put(open(file_path('logo-mongodb.png')))
        self.failUnlessRaises(File.ContentTypeUnspecified, file.save)

    def test_save(self):
        file = MediaFile()
        content_type = 'image/png'
        file.file.put(open(file_path('logo-mongodb.png')),
            content_type=content_type)
        file.save()
        file = MediaFile.objects.get(id=file.id)
        self.failUnlessEqual(content_type, file.file.content_type)
        self.failUnlessEqual(open(file_path('logo-mongodb.png')).read(),
                             file.file.read()
                             )

    def test_apply_transformations(self):
        file = MediaFile()
        file.file.put(open(file_path('logo-mongodb.png')),
            content_type='image/png')
        file.save()
        file.set_transformations(ImageResize(name='thumbnail', width=100, height=100))


    def test_apply_transformations_before_save_raises(self):
        pass