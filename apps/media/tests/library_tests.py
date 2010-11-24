# -*- coding: utf-8 -*-

import os

from django.test import TestCase

from apps.social.documents import Account

from ..library import *
from time import sleep

def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))

class LibraryTest(TestCase):
    def cleanUp(self):
        ImageLibrary.objects.delete()
        Account.objects.delete()

    def setUp(self):
        self.cleanUp()
        self.user1 = Account.create_user(username='user1', password='123')

    def test_get_common_library(self):
        library = ImageLibrary.get_common()
        self.failUnless(isinstance(library, ImageLibrary))


    def test_common_library_is_singleton(self):
        library1 = ImageLibrary.get_common()
        library2 = ImageLibrary.get_common()
        self.failUnlessEqual(library1, library2)

    def test_common_library_can_not_save_more_then_one(self):
        library1 = ImageLibrary(is_common=True)
        library1.save()
        
        library2 = ImageLibrary(is_common=True)
        self.failUnlessRaises(Exception, library2.save)

    def test_image_library(self):
        library = ImageLibrary(author=self.user1)
        library.save()

        file = ImageFile()
        content_type = 'image/png'
        file.file.put(open(file_path('logo-mongodb.png')),
            content_type=content_type)
        file.save()

        library.add(file)
        self.failUnlessRaises(Exception, library.save)

        library = ImageLibrary.objects.get(id=library.id)


