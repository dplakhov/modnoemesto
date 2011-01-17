# -*- coding: utf-8 -*-
import os

from lxml import etree

from mongoengine.document import Document
from mongoengine.fields import BooleanField, StringField, FileField, ReferenceField


class Theme(Document):
    name = StringField()
    description = StringField()
    is_public = BooleanField(default=False)

    class SourceFileNotExists(Exception):
        pass

    @classmethod
    def from_zip(cls, file):
        if not os.path.exists(file):
            raise Theme.SourceFileNotExists("File %s not exists" % file)
        theme = Theme()
        theme.save()
        return theme

    @classmethod
    def from_directory(cls, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Theme.SourceFileNotExists("Directory %s not exists" % directory)

        theme_xml = etree.parse(open(os.path.join(directory, 'theme.xml'))).getroot()

        theme = Theme()
        theme.is_public = theme_xml.attrib.get('public') == 'true'
        theme.name = theme_xml.attrib['name']
        theme.description = theme_xml.find('description').text.strip()

        theme.save()

        for file_name in os.listdir(directory):
            if file_name not in ('theme.xml', ):
                file = ThemeFile(theme=theme, name=file_name)
                ext = os.path.splitext(file_name)[-1][1:]
                content_types = {
                    'css': 'text/css',
                    'png': 'image/png',
                    'gif': 'image/gif',
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                }
                content_type = content_types[ext]
                file.file.put(open(os.path.join(directory, file_name)),
                              content_type=content_type)
                file.save()

        return theme

    @property
    def files(self):
        return ThemeFile.Proxy(self)

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
