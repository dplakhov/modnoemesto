# -*- coding: utf-8 -*-

import hachoir_core.config
hachoir_core.config.unicode_stdout = False
hachoir_core.config.quiet = True

from hachoir_core.stream.input import InputIOStream
from hachoir_parser import QueryParser

from hachoir_metadata import extractMetadata
from hachoir_metadata.riff import RiffMetadata
from hachoir_metadata.video import MovMetadata, AsfMetadata, FlvMetadata, MkvMetadata


class FileValidator(object):
    def validate(self, stream):
        raise NotImplementedError()

    class Exception(Exception):
        pass

    class UnrecognizedFormat(Exception):
        pass

    class IncorrectFormat(Exception):
        pass


class VideoFileValidator(object):
    def validate(self, stream):
        stream = InputIOStream(stream)
        query_parser = QueryParser([('category', 'video'),])
        parser = query_parser.parse(stream)
        metadata = extractMetadata(parser)
        if not metadata:
            raise FileValidator.UnrecognizedFormat('Unrecognized file format')

        if not isinstance(metadata,(
                RiffMetadata,
                MovMetadata,
                AsfMetadata,
                FlvMetadata,
                MkvMetadata,
                )):
            raise FileValidator.IncorrectFormat('Incorrect format')

