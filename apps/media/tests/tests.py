# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse


from django.test import TestCase
import mongoengine

from ..documents import *
from ..transformations.image import ImageResize

from .common import file_path, create_image_file


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
        TRANSFORMATION_NAME = 'thumbnail'
        file = create_image_file()
        (derivative, ) = file.apply_transformations(ImageResize(name=TRANSFORMATION_NAME,
                                             format='png', width=100, height=100))

        client = self.client
        response = client.get(reverse('media:file_view',
                           kwargs=dict(file_id=file.id,
                                  transformation_name=TRANSFORMATION_NAME)))


        self.assertEquals('image/png', response['Content-Type'])


class FileSetTest(TestCase):
    def test_add_file(self):
        file_set = FileSet(type='liba')
        file_set.save()

        file = create_image_file()

        file_set.add_file(file)
        
        self.failUnlessEqual(1, len(file_set.files))
        file_set.save()

        file_set.reload()
        self.failUnlessEqual(1, len(file_set.files))

    def test_add_file_without_save(self):
        file_set = FileSet(type='liba')
        file_set.save()

        file = create_image_file()

        file_set.add_file(file)
        
        self.failUnlessEqual(1, len(file_set.files))

        file_set.reload()
        self.failUnlessEqual(1, len(file_set.files))

    def test_remove_file(self):
        file_set = FileSet(type='liba')
        file_set.save()

        file1 = create_image_file()
        file2 = create_image_file()

        file_set.add_file(file1)
        file_set.add_file(file2)

        self.failUnlessEqual(2, len(file_set.files))

        file_set.remove_file(file1)
        self.failUnlessEqual(1, len(file_set.files))

        file_set.reload()
        self.failUnlessEqual(1, len(file_set.files))
