# -*- coding: utf-8 -*-

import tempfile
import shutil

class TemporaryDirectory(object):
    def __init__(self, suffix="", prefix=tempfile.template, dir=None):
        self.name = tempfile.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def __del__(self):
        shutil.rmtree(self.name, ignore_errors=True)
        