# -*- coding: utf-8 -*-
from base import Driver, StreamInterface, ControlInterface
from .exceptions import ImproperlyConfigured, AccessDenied
from mechanize import Browser, FormNotFoundError

class AxisStreamInterface(StreamInterface):
    pass

class AxisControlInterface(ControlInterface):

    def authenticate(self):
        try:
            client = Browser()
            client.set_handle_redirect(True)
            client.set_handle_robots(False)
            client.open('http://%s/cgi-bin/videoconfiguration.cgi' % self.camera.host)
            client.select_form('frmLOGON')
            client['LOGIN_ACCOUNT'] = self.camera.username
            client['LOGIN_PASSWORD'] = self.camera.password
            client.submit()

            try:
                client.select_form('frmLOGON')
            except FormNotFoundError:
                pass
            else:
                raise AccessDenied('Access denied for user `%s`' % self.camera.username)

        except AccessDenied:
            raise

        except Exception, e:
            raise ImproperlyConfigured(e.message)

        return client


    def check(self):
        super(AxisControlInterface, self).check()
        self.authenticate()
        return True


class AxisDriver(Driver):
    STREAM_INTERFACE_CLASS = AxisStreamInterface
    CONTROL_INTERFACE_CLASS = AxisControlInterface
