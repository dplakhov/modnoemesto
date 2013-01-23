# -*- coding: utf-8 -*-
import os
from ..documents import *

from ..transformations import FileTransformation

def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))

def create_image_file():
    file = File(type='test_image')
    file.file.put(open(file_path('logo-mongodb.png')),
        content_type='image/png')
    file.save()
    return file

def create_video_file(name=None):
    if name is None:
        name = 'flame.avi'
    file = File(type='image')
    file.file.put(open(file_path(name)),
        content_type='video/avi')
    file.save()
    return file

class TextTransformation(FileTransformation):
    def _apply(self, source, destination):
        source_data = int(source.file.read())

        destination.file.seek(0)
        destination.file.replace(str(source_data * 2),
                         content_type=destination.file.content_type)
        destination.save()
