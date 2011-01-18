# -*- coding: utf-8 -*-
import os
from lxml import etree
import zipfile

from mongoengine.document import Document
from mongoengine.fields import BooleanField, StringField, FileField, ReferenceField

class Theme(Document):
    name = StringField()
    description = StringField()
    is_public = BooleanField(default=False)

    class SourceFileNotExists(Exception):
        pass

    def _parse_meta(self, meta):
        theme_xml = etree.fromstring(meta)
        self.is_public = theme_xml.attrib.get('public') == 'true'
        self.name = theme_xml.attrib['name']
        self.description = theme_xml.find('description').text.strip()

    @classmethod
    def from_zip(cls, zip_file_name):
        if not os.path.exists(zip_file_name):
            raise Theme.SourceFileNotExists("File %s not exists" % zip_file_name)

        theme = Theme()
        file = zipfile.ZipFile(zip_file_name, 'r')
        theme._parse_meta(file.read('theme.xml').decode('utf-8'))
        theme.save()

        for file_name in file.namelist():
            if file_name not in ('theme.xml', ):
                theme.add_file(file_name, file.read(file_name))

        return theme

    @classmethod
    def from_directory(cls, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Theme.SourceFileNotExists("Directory %s not exists" % directory)

        theme = Theme()
        theme._parse_meta(open(os.path.join(directory, 'theme.xml')).read())
        theme.save()

        for file_name in os.listdir(directory):
            if file_name not in ('theme.xml', ):
                theme.add_file(file_name, open(os.path.join(directory, file_name)))

        return theme

    @property
    def files(self):
        return ThemeFile.Proxy(self)

    def add_file(self, file_name, stream):
        file = ThemeFile(theme=self, name=file_name)
        ext = os.path.splitext(file_name)[-1][1:]
        content_types = {
            'css': 'text/css',
            'png': 'image/png',
            'gif': 'image/gif',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
        }
        content_type = content_types[ext]
        file.file.put(stream, content_type=content_type)
        file.save()

class ThemeFile(Document):
    class Proxy(object):
        def __init__(self, theme):
            self.theme = theme

        def __getitem__(self, item):
            return ThemeFile.objects(theme=self.theme, name=item).first()

    theme = ReferenceField('Theme')
    name = StringField()
    file = FileField()

    def read(self, *args, **kwargs):
        return self.file.read(*args, **kwargs)
    
    @property
    def content_type(self):
        return self.file.content_type
