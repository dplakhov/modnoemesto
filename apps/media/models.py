# -*- coding: utf-8 -*-

from datetime import datetime

import cStringIO
from mongoengine import *

from ImageFile import Parser as ImageFileParser

class File(Document):
    author = ReferenceField('Account')
    ctime = DateTimeField()
    file = FileField()

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

    def create_derivatives(self):
        derivatives = []
        for trasformation in self.get_transformations():
            derivatives.append(trasformation.create_derivative(self))
        return derivatives

    def get_transformations(self):
        try:
            return self.trasformations
        except AttributeError:
            return []

class FileDerivative(Document):
    source = ReferenceField('File')
    file = FileField()

class FileTransformation(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def create_derivative(self, file):
        raise NotImplementedError


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

class ImageResize(FileTransformation):
    def create_derivative(self, source):
        derivative = FileDerivative(source=source)
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
