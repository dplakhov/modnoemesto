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
    author = ReferenceField('Account')
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
        if derivative:
            derivative = _get_db().dereference(derivative)
            derivative = File(**derivative)
            derivative.file = GridFSProxy(derivative.file)
            return derivative


class FileSet(Document):
    author = ReferenceField('Account')
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
