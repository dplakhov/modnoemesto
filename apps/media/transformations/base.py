# -*- coding: utf-8 -*-
import sys
import tempfile
import shlex
import subprocess

from django.conf import settings

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
                    type=self.type if hasattr(self, 'type') else source.type)


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
    CONTENT_TYPE =None
    
    class CommandNotFound(Exception):
        pass

    def _check_parameters(self):
        try:
            command = shlex.split(self.SYSTEM_COMMAND)[0]
            which.which(command)
        except which.WhichError, e:
            raise self.CommandNotFound(str(e))

    def _apply(self, source, destination):
        self._check_parameters()
        tmp_source = self._write_source(source)
        tmp_destination = self._create_destination()
        try:
            self._run_system_command(tmp_source, tmp_destination)
        except:
            raise

        self._read_destination(destination, tmp_destination)
        self._finalize()
        return destination

    def _write_source(self, source):
        file = tempfile.NamedTemporaryFile()
        file.file.write(source.file.read())
        file.file.seek(0)
        return file

    def _create_destination(self):
        return tempfile.NamedTemporaryFile()

    def _run_system_command(self, tmp_source, tmp_destination):
        command = self._format_system_command(tmp_source, tmp_destination)
        process = subprocess.Popen(shlex.split(command),
                                   stdin=subprocess.PIPE,
                                   stdout=sys.stdout if settings.DEBUG else subprocess.PIPE,
                                   stderr=sys.stderr if settings.DEBUG else subprocess.PIPE,
                                   )
        process.wait()

    def _format_system_command(self, tmp_source, tmp_destination):
        params = dict(source=tmp_source.name,
                      destination=tmp_destination.name)
        params.update(self.__class__.__dict__)
        params.update(self.__dict__)

        return self._get_system_command() % params

    def _get_system_command(self):
        return self.SYSTEM_COMMAND

    def _read_destination(self, destination, tmp_destination):
        tmp_destination.file.seek(0)
        destination.file.put(tmp_destination.file.read(),
                             content_type=self._get_derivative_content_type())
        destination.save()

    def _get_derivative_content_type(self):
        return self.CONTENT_TYPE

    def _finalize(self):
        pass
