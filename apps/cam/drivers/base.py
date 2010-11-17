# -*- coding: utf-8 -*-
from .exceptions import ImproperlyConfigured

class BaseInterface(object):
    def __init__(self, camera):
        self.camera = camera
    def check(self):
        for required in ('host', 'username', 'password'):
            if not getattr(self.camera, required):
                raise ImproperlyConfigured('Empty %s parameter' % required)


class ControlInterface(BaseInterface):
    def zoom_in(self):
        raise NotImplementedError()

    def zoom_out(self):
        raise NotImplementedError()

    def move_up(self):
        raise NotImplementedError()

    def move_down(self):
        raise NotImplementedError()

    def move_left(self):
        raise NotImplementedError()

    def move_right(self):
        raise NotImplementedError()

class StreamInterface(BaseInterface):
    def check(self):
       raise NotImplementedError()

    def enable(self):
        raise NotImplementedError()

    def disable(self):
        raise NotImplementedError()

class Driver(object):
    STREAM_INTERFACE_CLASS = StreamInterface
    CONTROL_INTERFACE_CLASS = ControlInterface

    _stream = None
    _control = None

    def __init__(self, camera):
        self.camera = camera

    @property
    def stream(self):
        if not self._stream:
            self._stream = self.STREAM_INTERFACE_CLASS(self.camera)
        return self._stream

    @property
    def control(self):
        if not self._control:
            self._control = self.CONTROL_INTERFACE_CLASS(self.camera)
        return self._control

