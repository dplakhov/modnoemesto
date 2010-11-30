# -*- coding: utf-8 -*-

from .base import FileTransformation
import Image

from ImageFile import Parser as ImageFileParser

from apps.utils.stringio import StringIO

class ImageResize(FileTransformation):
    FILE_TYPE = 'image'
    def _apply(self, source, destination):
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        image = source_image.resize((self.width, self.height,), Image.ANTIALIAS)
        buffer = StringIO()
        image.save(buffer, self.format)
        buffer.reset()
        destination.file.put(buffer, content_type = 'image/%s' % self.format)
        destination.save()
        return destination

