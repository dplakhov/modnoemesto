# -*- coding: utf-8 -*-
from base import Driver, StreamInterface, ControlInterface
from mechanize import Browser

class AxisStreamInterface(StreamInterface):
    pass

class AxisControlInterface(ControlInterface):
    @property
    def url(self):
        return 'http://' + self.camera.host

    def check(self):
        super(AxisControlInterface, self).check()
        client = Browser()
        client.add_password(self.url, self.camera.username, self.camera.password)
        client.open(self.url)


class AxisDriver(Driver):
    STREAM_INTERFACE_CLASS = AxisStreamInterface
    CONTROL_INTERFACE_CLASS = AxisControlInterface