# -*- coding: utf-8 -*-

from django.test import TestCase
from apps.utils.stringio import StringIO

from ..documents import *
from ..transformations import BatchFileTransformation, SystemCommandFileTransformation
from ..transformations.image import ImageResize
from ..transformations.video import VideoThumbnail

from .common import file_path, create_image_file, create_video_file, TextTransformation


class FileTransformationTest(TestCase):
    def test_apply_transformations(self):

        TRANSFORMATION_NAME = 'thumbnail'

        file = create_image_file()

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


class SystemCommandFileTransformationTest(TestCase):
    def test_system_command_transformations(self):
        class TestSystemCommandFileTransformation(SystemCommandFileTransformation):
            FILE_TYPE = 'text'
            SYSTEM_COMMAND = 'cp %(source)s %(destination)s'
            def _get_derivative_content_type(self):
                return 'text/plain'


        file = File(type='text')
        buffer = StringIO()
        buffer.write('1')
        buffer.reset()
        file.file.put(buffer, content_type='text/plain')
        file.save()
        file.reload()

        transformation = TestSystemCommandFileTransformation('test_trans')
        transformation.apply(file)
        derivative = file.get_derivative('test_trans')
        self.failUnlessEqual('1', derivative.file.read())
        self.failUnlessEqual('text/plain', derivative.file.content_type)

    def test_unknown_command_raises_exc_(self):
        class TestSystemCommandFileTransformation(SystemCommandFileTransformation):
            FILE_TYPE = 'text'
            SYSTEM_COMMAND = 'bzzzzzzzZ %(source)s %(destination)s'
        self.failUnlessRaises(SystemCommandFileTransformation.CommandNotFound,
                              TestSystemCommandFileTransformation, 'name')    


class VideoFileTransformationTest(TestCase):
    def test_video_thumbnail(self):
        file = create_video_file()
        transformation = VideoThumbnail(name='thumb.png', format='png')
        thumb = transformation.apply(file)
        self.failUnlessEqual('image/png', thumb.file.content_type)
        self.failUnless(str(thumb.file.read()[1:]).startswith('PNG'))


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

        file = create_image_file()

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

