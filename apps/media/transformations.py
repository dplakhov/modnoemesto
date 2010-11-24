# -*- coding: utf-8 -*-

import Image


from ImageFile import Parser as ImageFileParser
from .documents import File

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO



class FileTransformation(object):
    def __init__(self, name, **kwargs):
        self.name = name
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, source):
        raise NotImplementedError

    def create_derivative(self, source):
        return File(source=source, transformation=self.name, type=self.FILE_TYPE)


class BatchFileTransformation(FileTransformation):
    pass

class ImageResize(FileTransformation):
    FILE_TYPE = 'image'
    def apply(self, source):
        derivative = self.create_derivative(source)
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        image = source_image.resize((self.width, self.height,), Image.ANTIALIAS)
        buffer = StringIO()
        image.save(buffer, self.format)
        buffer.reset()
        derivative.file.put(buffer, content_type = 'image/%s' % self.format)
        derivative.save()
        return derivative

class VideoThumbnail(FileTransformation):
    pass

