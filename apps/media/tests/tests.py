# -*- coding: utf-8 -*-

import os

from django.test import TestCase

from ..documents import *
from ..transformations import ImageResize
import mongoengine

def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))


class FileTest(TestCase):
    def test_save_empty_file_raises_exc(self):
        file = File(type='image')
        self.failUnlessRaises(File.SourceFileEmpty, file.save)

    def test_save_type_unspecified_raises_exc(self):
        file = File()
        content_type = 'image/png'
        file.file.put(open(file_path('logo-mongodb.png')),
            content_type=content_type)
        self.failUnlessRaises(mongoengine.ValidationError, file.save)

    def test_save_content_type_unspecified_raises_exc(self):
        file = File(type='image')
        file.file.put(open(file_path('logo-mongodb.png')))
        self.failUnlessRaises(File.ContentTypeUnspecified, file.save)

    def test_save(self):
        file = File(type='image')
        content_type = 'image/png'
        file.file.put(open(file_path('logo-mongodb.png')),
            content_type=content_type)
        file.save()
        file = File.objects.get(id=file.id)
        self.failUnlessEqual(content_type, file.file.content_type)
        self.failUnlessEqual(open(file_path('logo-mongodb.png')).read(),
                             file.file.read()
                             )

    def test_apply_transformations(self):

        TRANSFORMATION_NAME = 'thumbnail'

        file = File(type='image')

        file.file.put(open(file_path('logo-mongodb.png')),
            content_type='image/png')

        file.save()

        file = File(id=file.id)
        file.reload()

        derivatives = file.apply_transformations(ImageResize(name=TRANSFORMATION_NAME,
                                             format='png', width=100, height=100))

        self.failUnless(derivatives)
        self.failUnlessEqual(type({}), type(derivatives))
        self.failUnlessEqual(1, len(derivatives))

        derivative = derivatives[TRANSFORMATION_NAME]
        derivative = File.objects(id=derivative.id).first()

        self.failUnless(isinstance(derivative, File))
        self.failUnless(derivative.file.read())

        self.failUnless(file.derivatives)

        self.failUnlessEqual(derivative.file.read(),
                             file.get_derivative(TRANSFORMATION_NAME).file.read())

        self.failUnlessEqual(derivative.file.content_type, 'image/png')

        derivative = file.get_derivative(TRANSFORMATION_NAME)


        self.failUnlessEqual(TRANSFORMATION_NAME, derivative.transformation)

        self.failUnless(file.get_derivative('notfound') is None)

    def test_apply_transformations_before_save_raises_exc(self):
        pass


class TasksTest(TestCase):
    def test_apply_file_transformations(self):
        print '\nthis test requres running celeryd (python manage.py celeryd test)'
        from ..tasks import apply_file_transformations
        file = File(type='image')

        file.file.put(open(file_path('logo-mongodb.png')),
            content_type='image/png')

        file.save()

        args = [
            str(file.id),
            ImageResize(name='trans1', format='png', width=100, height=100),
            ImageResize(name='trans2', format='png', width=100, height=100)
        ]

        result = apply_file_transformations.apply_async(args=args)
        result.get()

        file.reload()

        self.failUnless(file.get_derivative('trans1'))
        self.failUnless(file.get_derivative('trans2'))


class FileSetTest(TestCase):
    pass