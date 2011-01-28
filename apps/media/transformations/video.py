# -*- coding: utf-8 -*-

import os

from apps.utils import tempdir

from .base import SystemCommandFileTransformation

class VideoThumbnail(SystemCommandFileTransformation):
    SYSTEM_COMMAND = '''mplayer -ss 2 -frames 1 -vo %(format)s:outdir=%(destination)s:z=%(compression)s -nosound %(source)s'''

    compression = 0

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

class MAYBE_VideoThumbnail(SystemCommandFileTransformation):
    CONTENT_TYPE = 'image/jpeg'
    SYSTEM_COMMAND = '''ffmpeg -i %(source)s -an -ss 00:00:10 -r 1 -vframes 1 -y -f mjpeg  %(destination)s'''

class Video2Flv(SystemCommandFileTransformation):
    CONTENT_TYPE = 'video/x-flv'
    _SYSTEM_COMMAND = '''mencoder %(source)s -o %(destination)s -of lavf -oac mp3lame -lameopts abr:br=56 -srate 22050 -ovc lavc -lavcopts vcodec=flv:vbitrate=500:mbd=2:mv0:trell:v4mv:cbp:last_pred=3'''
    SYSTEM_COMMAND = '''ffmpeg -y -i %(source)s -f flv %(destination)s'''