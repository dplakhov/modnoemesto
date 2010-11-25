# -*- coding: utf-8 -*-

import os
from django.core.urlresolvers import reverse

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.test import TestCase
import mongoengine

from ..documents import *
from ..transformations import FileTransformation, BatchFileTransformation
from ..transformations.image import ImageResize

def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))

def create_file():
    file = File(type='image')
    file.file.put(open(file_path('logo-mongodb.png')),
        content_type='image/png')
    file.save()
    return file

class TextTransformation(FileTransformation):
    def _apply(self, source, destination):
        source_data = int(source.file.read())

        destination.file.seek(0)
        destination.file.replace(str(source_data * 2),
                         content_type=destination.file.content_type)
        destination.save()

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

class FileViewTest(TestCase):
    def test_view_derivative(self):
        print reverse('media:file_view', kwargs={'transformation_name':
                                                 u'thumb', 'file_id': u'4ced41403633844b9e000003'})
        TRANSFORMATION_NAME = 'thumbnail'
        file = create_file()
        (derivative, ) = file.apply_transformations(ImageResize(name=TRANSFORMATION_NAME,
                                             format='png', width=100, height=100))

        client = self.client
        response = client.get(reverse('media:file_view',
                           kwargs=dict(file_id=file.id,
                                  transformation_name=TRANSFORMATION_NAME)))


        self.assertEquals('image/png', response['Content-Type'])

class FileTransformationTest(TestCase):
    def test_apply_transformations(self):

        TRANSFORMATION_NAME = 'thumbnail'

        file = create_file()

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

        self.failUnlessEqual(file, derivative.source)

        self.failUnlessRaises(File.DerivativeNotFound, file.get_derivative, 'notfound')

        derivative = file.modifications[TRANSFORMATION_NAME]
        self.failUnlessEqual(file, derivative.source)


    def test_apply_transformations_before_save_raises_exc(self):
        file = File(type='image')

        file.file.put(open(file_path('logo-mongodb.png')),
            content_type='image/png')

        self.failUnlessRaises(Exception, file.apply_transformations,
                              ImageResize(name='thumbnail',
                                          format='png', width=100, height=100))

    def test_apply_transformation_into_source(self):
        file = File(type='text')
        buffer = StringIO()
        buffer.write('1')
        buffer.reset()
        file.file.put(buffer, content_type='text/plain')
        file.save()
        file.reload()
        self.failUnlessEqual('1', file.file.read())


        transformation = TextTransformation('test')
        transformation.apply(file, file)

        file.reload()
        self.failUnlessEqual('2', file.file.read())

        transformation.apply(file, file)
        file.reload()
        self.failUnlessEqual('4', file.file.read())

class BatchFileTransformationTest(TestCase):
    def test_batch_transformation_with_single_transformation(self):
        file = File(type='text')
        buffer = StringIO()
        buffer.write('1')
        buffer.reset()
        file.file.put(buffer, content_type='text/plain')
        file.save()
        file.reload()

        transformation = BatchFileTransformation('batch',
                    TextTransformation('test')
                )

        transformation.apply(file, file)

        file.reload()
        self.failUnlessEqual('2', file.file.read())

    def test_batch_transformation_with_multiple_transformations(self):
        file = File(type='text')
        buffer = StringIO()
        buffer.write('1')
        buffer.reset()
        file.file.put(buffer, content_type='text/plain')
        file.save()
        file.reload()

        transformation = BatchFileTransformation('batch',
                    TextTransformation('test'),
                    TextTransformation('test'),
                    TextTransformation('test')
                )

        transformation.apply(file, file)

        file.reload()
        self.failUnlessEqual('8', file.file.read())

    def test_batch_transformation_constructor_exc(self):
        self.failUnlessRaises(Exception, BatchFileTransformation, 'batch')
        self.failUnlessRaises(Exception, BatchFileTransformation, 'batch',
                              'not Transformation class')


class TransformationTasksTest(TestCase):
    def test_apply_file_transformations(self):
        print '\nthis test requres running celeryd (python manage.py celeryd test)'
        from ..tasks import apply_file_transformations

        file = create_file()

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
    def test_add_file(self):
        file_set = FileSet(type='liba')
        file_set.save()

        file = create_file()

        file_set.add_file(file)
        
        self.failUnlessEqual(1, len(file_set.files))
        file_set.save()

        file_set.reload()
        self.failUnlessEqual(1, len(file_set.files))

    def test_add_file_without_save(self):
        file_set = FileSet(type='liba')
        file_set.save()

        file = create_file()

        file_set.add_file(file)
        
        self.failUnlessEqual(1, len(file_set.files))

        file_set.reload()
        self.failUnlessEqual(1, len(file_set.files))
        