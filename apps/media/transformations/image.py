# -*- coding: utf-8 -*-

from .base import FileTransformation
import Image

from ImageFile import Parser as ImageFileParser

from apps.utils.stringio import StringIO

class ImageResize(FileTransformation):
    def _apply(self, source, destination):
        parser = ImageFileParser()
        parser.feed(source.file.read())
        source_image = parser.close()
        crop_box = self._get_crop_box(source_image.size,
                                      (self.width, self.height))
        image = source_image.crop(crop_box)
        image = image.resize((self.width, self.height), Image.ANTIALIAS)
        buffer = StringIO()
        image.save(buffer, self.format)
        buffer.reset()
        if destination.file:
            write = destination.file.replace
        else:
            write = destination.file.put

        write(buffer, content_type = 'image/%s' % self.format)

        destination.save()
        return destination

    def _get_crop_box(self, source, destination):
        wo, ho = source
        wr, hr = destination
        ko = float(wo)/ho
        kr = float(wr)/hr
        if ko < kr:
            wc = wo
            hc = wo*hr/wr
            lc = 0
            tc = (ho - hc)/2
        elif ko > kr:
            wc = ho*wr/hr
            hc = ho
            lc = (wo - wc)/2
            tc = 0
        else:
            wc = wo
            hc = ho
            lc = 0
            tc = 0
        return lc, tc, lc + wc, tc + hc