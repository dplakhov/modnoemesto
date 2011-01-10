# -*- coding: utf-8 -*-
import os
from ..documents import *

def file_path(file_name):
    return os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        'files', file_name))

def create_file():
    file = File(type='test_image')
    file.file.put(open(file_path('logo-mongodb.png')),
        content_type='image/png')
    file.save()
    return file
