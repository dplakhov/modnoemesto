# -*- coding: utf-8 -*-

import os

from apps.utils import tempdir

from .base import SystemCommandFileTransformation

class VideoThumbnail(SystemCommandFileTransformation):
    FILE_TYPE = 'image'
    SYSTEM_COMMAND = '''mplayer -ss 2 -frames 1 -vo %(format)s:outdir=%(destination)s -nosound %(source)s'''

    def _create_destination(self):
        return tempdir.TemporaryDirectory()

    def _read_destination(self, destination, tmp_destination):
        directory = tmp_destination.name
        files = os.listdir(directory)
        assert len(files) == 1
        file = open(os.path.join(directory, files[0]), 'rb')
        destination.file.put(file.read(),
                             content_type=self._get_derivative_content_type())
        destination.save()

    def _get_derivative_content_type(self):
        return 'image/%s' % self.format
