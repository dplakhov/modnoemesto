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

from ImageFile import Parser as ImageFileParser

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
    
    def save(self):
        if self.file.read() is None:
            raise File.SourceFileEmpty()

        if self.file.content_type is None:
            raise File.ContentTypeUnspecified()

        super(File, self).save()

    def set_transformations(self, *trasformations):
        if trasformations:
            self.trasformations = trasformations

    def apply_transformations(self):
        derivatives = {}

        for trasformation in self.get_transformations():
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
        derivative = self.derivatives[transformation_name]
        if derivative:
            derivative = _get_db().dereference(derivative)
            derivative = FileDerivative(**derivative)
            derivative.file = GridFSProxy(derivative.file)
            return derivative

class FileDerivative(Document):
    source = ReferenceField('File')
    file = FileField()
    transformation = StringField()

class FileTransformation(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, source):
        raise NotImplementedError

    def create_derivative(self, source):
        return FileDerivative(source=source, transformation=self.name)


class BatchFileTransformation(FileTransformation):
    pass

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

class ImageResize(FileTransformation):
    def apply(self, source):
        derivative = self.create_derivative(source)
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        image = source_image.resize((self.width, self.height,))
        image.save(derivative.file, self.format)
        derivative.file.content_type = 'image/%s' % self.format
        derivative.file.close()
        derivative.save()
        return derivative

class VideoThumbnail(FileTransformation):
    pass

