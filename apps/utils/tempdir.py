# -*- coding: utf-8 -*-

import tempdir
import shutil

class TemporaryDirectory(object):
    def __init__(self, suffix="", prefix=tempdir.template, dir=None):
        self.name = tempdir.mkdtemp(suffix=suffix, prefix=prefix, dir=dir)

    def __del__(self):
        shutil.rmtree(self.name, ignore_errors=True)
        