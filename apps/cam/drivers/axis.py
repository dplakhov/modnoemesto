# -*- coding: utf-8 -*-
from base import Driver, StreamInterface, ControlInterface


class AxisStreamInterface(StreamInterface):
    pass

class AxisControlInterface(ControlInterface):
    pass

class AxisDriver(Driver):
    STREAM_INTERFACE_CLASS = AxisStreamInterface
    CONTROL_INTERFACE_CLASS = AxisControlInterface