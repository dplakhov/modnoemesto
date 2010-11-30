# -*- coding: utf-8 -*-

from .base import SystemCommandFileTransformation

class VideoThumbnail(SystemCommandFileTransformation):
    CONTENT_TYPE = 'image/jpeg'
    SYSTEM_COMMAND = '''ffmpeg -itsoffset -4 -i %(source)s -vcodec mjpeg -vframes 1 -an -f rawvideo -s 320x240 %(destination)s'''
