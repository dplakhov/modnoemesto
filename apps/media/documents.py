# -*- coding: utf-8 -*-

from datetime import datetime

import pymongo.dbref

from mongoengine import Document

from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import FileField
from mongoengine import DictField
from mongoengine import StringField
from mongoengine import ListField

from mongoengine.connection import _get_db
from mongoengine.fields import GridFSProxy

class File(Document):
    author = ReferenceField('User')
    type = StringField(regex='^\w+$', required=True)
    ctime = DateTimeField()
    file = FileField()

    derivatives = DictField()
    source = ReferenceField('File')
    transformation = StringField()

    meta = {
        'indexes': [
                'author',
                'type',
                'source',
        ],
    }

    class SourceFileEmpty(Exception):
        pass

    class ContentTypeUnspecified(Exception):
        pass

    class DerivativeNotFound(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super(File, self).__init__(*args, **kwargs)
        self.ctime = self.ctime or datetime.now()

    def save(self, *args, **kwargs):
        if self.file.read() is None:
            raise File.SourceFileEmpty()

        if self.file.content_type is None:
            raise File.ContentTypeUnspecified()

        super(File, self).save(*args, **kwargs)


    def apply_transformations(self, *transformations):
        derivatives = {}

        for transformation in transformations:
            derivatives[transformation.name] = transformation.apply(self)

        if derivatives:
            for name, derivative in derivatives.items():
                self.derivatives[name] = pymongo.dbref.DBRef(derivative._meta['collection'],
                                                             derivative.pk)
            self.save()

        return derivatives

    def get_derivative(self, transformation_name):
        derivative = self.derivatives.get(transformation_name)

        if not derivative:
            raise File.DerivativeNotFound()

        derivative = _get_db().dereference(derivative)
        derivative = File(**derivative)
        derivative.file = GridFSProxy(derivative.file)
        return derivative

    class DerivativeProxy(object):
        def __init__(self, file):
            self.file = file

        def __getitem__(self, item):
            return self.file.get_derivative(item)

    def __getattribute__(self, item):
        if item == 'modifications':
            return File.DerivativeProxy(self)
        return super(File, self).__getattribute__(item)


class FileSet(Document):
    author = ReferenceField('User')
    name = StringField()
    type = StringField(regex='^\w+$', required=True)
    files = ListField(ReferenceField(File))

    meta = {
        'indexes': [
                'author',
                'type',
        ],
    }


    def add_file(self, file):
        self.files.append(file)
        self.__class__.objects(id=self.id).update_one(push__files=file)


