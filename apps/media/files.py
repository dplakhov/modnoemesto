# -*- coding: utf-8 -*-

from datetime import datetime

import pymongo.dbref

from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import FileField
from mongoengine import DictField
from mongoengine import StringField

from mongoengine.connection import _get_db
from mongoengine.fields import GridFSProxy


class File(Document):
    author = ReferenceField('Account')
    ctime = DateTimeField()
    file = FileField()
    derivatives = DictField()

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

    def set_transformations(self, *trasformations):
        if trasformations:
            self.trasformations = trasformations

    def apply_transformations(self, *args):
        derivatives = {}

        transformations = args if args else self.get_transformations()

        for trasformation in transformations:
            derivatives[trasformation.name] = trasformation.apply(self)

        if derivatives:
            for name, derivative in derivatives.items():
                self.derivatives[name] = pymongo.dbref.DBRef(derivative._meta['collection'],
                                                                           derivative.pk)
            self.save()

        return derivatives

    def get_transformations(self):
        try:
            return self.trasformations
        except AttributeError:
            return []

    def get_derivative(self, transformation_name):
        derivative = self.derivatives.get(transformation_name)
        if derivative:
            derivative = _get_db().dereference(derivative)
            derivative = FileDerivative(**derivative)
            derivative.file = GridFSProxy(derivative.file)
            return derivative

class FileDerivative(Document):
    source = ReferenceField('File')
    file = FileField()
    transformation = StringField()


class MediaFile(File):
    pass

############################################################################################

class ImageFile(MediaFile):
    pass

class VideoFile(MediaFile):
    pass

class AudioFile(MediaFile):
    pass


############################################################################################

