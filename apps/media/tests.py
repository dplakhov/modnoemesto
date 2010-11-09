from django.test import TestCase
import urllib
from models import *

class MediaTest(TestCase):
    def test_save_empty_file_raises(self):
        file = MediaFile()
        self.failUnlessRaises(File.SourceFileEmpty, file.save)


    def test_save_content_type_unspecified_raises(self):
        file = MediaFile()
        file.file.replace(urllib.urlopen('http://www.google.ru/images/srpr/nav_logo14.png'))
        self.failUnlessRaises(File.ContentTypeUnspecified, file.save)



