# -*- coding: utf-8 -*-
from base import Driver, StreamInterface, ControlInterface
from .exceptions import ImproperlyConfigured, AccessDenied

class TelnewStreamInterface(StreamInterface):
    pass

class TelnewControlInterface(ControlInterface):
    pass

class TelnewDriver(Driver):
    STREAM_INTERFACE_CLASS = TelnewStreamInterface
    CONTROL_INTERFACE_CLASS = TelnewControlInterface

    template = 'cam/views/telnew.html'
