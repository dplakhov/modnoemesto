# -*- coding: utf-8 -*-

import os


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
        file.set_transformations(ImageResize(name='thumbnail', format='png', width=100, height=100))
        derivatives = file.create_derivatives()

        self.failUnless(derivatives)
        self.failUnlessEqual(type([]), type(derivatives))
        self.failUnlessEqual(1, len(derivatives))

        derivative = derivatives[0]
        print derivative.file.content_type

        self.failUnless(isinstance(derivative, FileDerivative))
        self.failUnless(derivative.file.read())


    def test_apply_transformations_before_save_raises(self):
        pass