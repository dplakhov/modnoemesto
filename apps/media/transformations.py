# -*- coding: utf-8 -*-

import Image


from ImageFile import Parser as ImageFileParser
from .documents import File

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO



class FileTransformation(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.args = args
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, source, destination=None):
        if destination is None:
            destination = self.create_derivative(source)
        return self._apply(source, destination)

    def _apply(self, source, destination):
        raise NotImplementedError

    def create_derivative(self, source):
        return File(source=source, transformation=self.name,
                    type=self.FILE_TYPE)


class BatchFileTransformation(FileTransformation):
    def __init__(self, name, *args, **kwargs):
        assert len(args)

        for transformation in args:
            assert isinstance(transformation, FileTransformation)

        self.transformations = args

        super(BatchFileTransformation, self).__init__(name, *args, **kwargs)

    def _apply(self, source, destination):
        for i, transformation in enumerate(self.transformations):
            transformation.apply(source, destination)
            if not i:
                source = destination

class ImageResize(FileTransformation):
    FILE_TYPE = 'image'
    def _apply(self, source, destination):
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        image = source_image.resize((self.width, self.height,), Image.ANTIALIAS)
        buffer = StringIO()
        image.save(buffer, self.format)
        buffer.reset()
        destination.file.put(buffer, content_type = 'image/%s' % self.format)
        destination.save()
        return destination

class VideoThumbnail(FileTransformation):
    pass

