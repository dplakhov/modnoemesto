# -*- coding: utf-8 -*-
import os
from lxml import etree
import re
import zipfile

from mongoengine.document import Document
from mongoengine.fields import BooleanField, StringField, FileField, ReferenceField

from apps.utils.stringio import StringIO

class Theme(Document):
    name = StringField(unique=True)
    description = StringField()
    is_public = BooleanField(default=False)
    html_top = StringField()

    class SourceFileNotExists(Exception):
        pass

    def delete(self, *args, **kwargs):
        self.delete_files()
        super(Theme, self).delete(*args, **kwargs)

    def delete_files(self):
        ThemeFile.objects(theme=self).delete()
        ThemeTemplate.objects(theme=self).delete()

    @classmethod
    def _get_or_create(cls, meta):
        theme_xml = etree.fromstring(meta)
        name = theme_xml.attrib['name']
        theme, created = Theme.objects.get_or_create(name=name)
        theme.is_public = theme_xml.attrib.get('public') == 'true'
        theme.description = theme_xml.find('description').text.strip()
        if not created:
            theme.delete_files()
            theme.html_top = None

        html_top = theme_xml.find('html_top')

        if html_top is not None:
            text = html_top.text.strip()
            text = re.sub(r' src="/.*?([\w.]+)"',
                          r' src="/theme/%s/\1"' % theme.id,
                          text)

            theme.html_top = text

        theme.save()

        return theme


    @classmethod
    def from_zip(cls, zip_file_name):
        if not os.path.exists(zip_file_name):
            raise Theme.SourceFileNotExists("File %s not exists" % zip_file_name)

        file = zipfile.ZipFile(zip_file_name, 'r')
        theme = Theme._get_or_create(file.read('theme.xml').decode('utf-8'))

        for file_name in file.namelist():
            if cls._is_valid_theme_subfile(file_name):
                theme.add_file(file_name, file.read(file_name))
            elif file_name.startswith('templates') and not file_name.endswith('/'):
                theme.add_template_file(file_name.replace('templates/', ''),
                                        StringIO(file.read(file_name)))

        return theme

    @classmethod
    def from_directory(cls, directory):
        if not os.path.exists(directory) or not os.path.isdir(directory):
            raise Theme.SourceFileNotExists("Directory %s not exists" % directory)

        theme = Theme._get_or_create(open(os.path.join(directory, 'theme.xml')).read())

        for file_name in os.listdir(directory):
            if cls._is_valid_theme_subfile(file_name):
                theme.add_file(file_name, open(os.path.join(directory, file_name)))

        template_dir = os.path.join(directory, 'templates') + os.path.sep
        if os.path.exists(template_dir) and os.path.isdir(template_dir):
            for root, dirs, files in os.walk(template_dir):
                if not files:
                    continue
                for file in files:
                    file_name = os.path.join(template_dir, root, file)
                    template_name = file_name.replace(template_dir, '')
                    theme.add_template_file(template_name, open(file_name))

        return theme

    @classmethod
    def _is_valid_theme_subfile(cls, file_name):
        return file_name not in ('theme.xml', ) and not file_name.startswith('templates')

    @property
    def files(self):
        return ThemeFile.Proxy(self)

    @property
    def templates(self):
        return ThemeTemplate.Proxy(self)

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

    def add_template_file(self, template_name, stream):
        template = ThemeTemplate(theme=self, name=template_name)
        template.content = stream.read()
        template.save()

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

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super(ThemeFile, self).delete(*args, **kwargs)

class ThemeTemplate(Document):
    class Proxy(object):
        def __init__(self, theme):
            self.theme = theme

        def __getitem__(self, item):
            return ThemeTemplate.objects(theme=self.theme, name=item).first()

    theme = ReferenceField('Theme')
    name = StringField()
    content = StringField()