# -*- coding: utf-8 -*-
import os

from lxml import etree

from mongoengine.document import Document
from mongoengine.fields import BooleanField, StringField

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

        return theme

    