# -*- coding: utf-8 -*-
from base import Driver, StreamInterface, ControlInterface
from .exceptions import ImproperlyConfigured, AccessDenied
from mechanize import Browser, FormNotFoundError

class AxisStreamInterface(StreamInterface):
    pass

class AxisControlInterface(ControlInterface):
    CMD_ZOOM_IN = 'ZOOM=TELE,5'
    CMD_ZOOM_OUT = 'ZOOM=WIDE,5'

    CMD_MOVE_UP = 'MOVE=UP,1'
    CMD_MOVE_DOWN = 'MOVE=DOWN,1'
    CMD_MOVE_LEFT = 'MOVE=LEFT,1'
    CMD_MOVE_RIGHT = 'MOVE=RIGHT,1'

    CMD_HOME = 'MOVE=HOME,'
    CMD_RESET = 'MOVE=RESET,'

    CMD_STOP_MOVE = 'MOVE=STOP,1,1'
    CMD_STOP_ZOOM = 'ZOOM=STOP,5'


    _client = None

    def authenticate(self):
        if self._client:
            return self._client

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

        self._client = client
        return client

    # @raise AccessDenied, ImproperlyConfigured
    def check(self):
        super(AxisControlInterface, self).check()
        self.authenticate()
        return True

    def control_url(self, command):
        return 'http://%(host)s/cgi-bin/encoder?USER=%(username)s&PWD=%(password)s&%(command)s' % \
        dict(
                host=self.camera.host,
                username=self.camera.username,
                password=self.camera.password,
                command=command
                )

    def zoom_in(self):
        self.authenticate().open(self.control_url(self.CMD_ZOOM_IN))
        self._stop_zoom()

    def zoom_out(self):
        self.authenticate().open(self.control_url(self.CMD_ZOOM_OUT))
        self._stop_zoom()

    def move_up(self):
        self.authenticate().open(self.control_url(self.CMD_MOVE_UP))
        self._stop_move()

    def move_down(self):
        self.authenticate().open(self.control_url(self.CMD_MOVE_DOWN))
        self._stop_move()

    def move_left(self):
        self.authenticate().open(self.control_url(self.CMD_MOVE_LEFT))
        self._stop_move()

    def move_right(self):
        self.authenticate().open(self.control_url(self.CMD_MOVE_RIGHT))
        self._stop_move()

    def home(self):
        self.authenticate().open(self.control_url(self.CMD_HOME))
        self._stop_move()

    def reset(self):
        self.authenticate().open(self.control_url(self.CMD_RESET))
        self._stop_move()

    def _stop_move(self):
        self.authenticate().open(self.control_url(self.CMD_STOP_MOVE))

    def _stop_zoom(self):
        self.authenticate().open(self.control_url(self.CMD_STOP_ZOOM))



class AxisDriver(Driver):
    STREAM_INTERFACE_CLASS = AxisStreamInterface
    CONTROL_INTERFACE_CLASS = AxisControlInterface
