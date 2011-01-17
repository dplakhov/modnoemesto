# -*- coding: utf-8 -*-
from .documents import *
import os
from mongoengine.document import Document

class Theme(Document):
    class SourceFileNotExists(Exception):
        pass

    @classmethod
    def from_zip(cls, file):
        if not os.path.exists(file):
            raise Theme.SourceFileNotExists("File %s not exists" % file)
        pass