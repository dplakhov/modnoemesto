# -*- coding: utf-8 -*-

import tempfile
import shlex
import subprocess

from apps.utils import which

from ..documents import File

class FileTransformation(object):
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.kwargs = kwargs
        self.args = args
        for k, v in kwargs.items():
            setattr(self, k, v)

    def apply(self, source, destination=None):
        if destination is None:
            destination = self.create_derivative(source)
        return self._apply(source, destination)

    def _apply(self, source, destination):
        raise NotImplementedError

    def create_derivative(self, source):
        return File(source=source, transformation=self.name,
                    type=self.FILE_TYPE)


class BatchFileTransformation(FileTransformation):
    def __init__(self, name, *args, **kwargs):
        assert len(args)

        for transformation in args:
            assert isinstance(transformation, FileTransformation)

        self.transformations = args

        super(BatchFileTransformation, self).__init__(name, *args, **kwargs)

    def _apply(self, source, destination):
        for i, transformation in enumerate(self.transformations):
            transformation.apply(source, destination)
            if not i:
                source = destination



class SystemCommandFileTransformation(FileTransformation):
    SYSTEM_COMMAND = None

    class CommandNotFound(Exception):
        pass

    def __init__(self, name, *args, **kwargs):
        try:
            command = shlex.split(self.SYSTEM_COMMAND)[0]
            which.which(command)
        except which.WhichError, e:
            raise self.CommandNotFound(str(e))

        super(SystemCommandFileTransformation, self).__init__(name, *args, **kwargs)

    def _apply(self, source, destination):
        source_tmp_file = self._write_source(source)
        destination_tmp_file = self._create_destination()
        try:
            self._run_system_command(source, destination, source_tmp_file, destination_tmp_file)
        except:
            raise

        self._write_destination(destination, destination_tmp_file)
        return destination

    def _write_source(self, source):
        file = tempfile.NamedTemporaryFile()
        file.file.write(source.file.read())
        file.file.seek(0)
        return file

    def _create_destination(self):
        file = tempfile.NamedTemporaryFile()
        return file

    def _run_system_command(self, source, destination, source_tmp_file, destination_tmp_file):
        command = self.SYSTEM_COMMAND % dict(source=source_tmp_file.name,
                                             destination=destination_tmp_file.name)
        process = subprocess.Popen(shlex.split(command))
        process.wait()

    def _write_destination(self, destination, destination_tmp_file):
        destination_tmp_file.file.seek(0)
        destination.file.put(destination_tmp_file.file.read(), content_type = 'image/png')
        destination.save()
