# -*- coding: utf-8 -*-

from ..documents import File

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


class VideoThumbnail(FileTransformation):
    pass

