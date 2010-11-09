# -*- coding: utf-8 -*-

from datetime import datetime

from mongoengine import *



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


class FileDerivation(Document):
    source = ReferenceField('File')
    file = FileField()


class FileTransformation(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.kwargs = kwargs

class ImageResize(FileTransformation):
    pass


class BatchFileTransformation(FileTransformation):
    pass


class MediaFile(File):
    pass

class ImageFile(MediaFile):
    pass



