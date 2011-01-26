# -*- coding: utf-8 -*-
from hachoir_core.stream.input import InputIOStream
import hachoir_metadata
import hachoir_parser
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
        query_parser = hachoir_parser.QueryParser([('category', 'video'),])
        parser = query_parser.parse(stream)
        metadata = hachoir_metadata.extractMetadata(parser)
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

