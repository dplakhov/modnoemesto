# -*- coding: utf-8 -*-
from django.test import TestCase

import apps.cam.drivers.axis
from models import CameraType, Camera

class CameraDriverTest(TestCase):
    def test_driver_class_loading(self):
        camera_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        self.failUnlessEqual(apps.cam.drivers.axis.AxisDriver,
                             camera_type.driver_class
                             )

    def test_driver_class_instantiation(self):
        camera_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        camera = Camera(type=camera_type)
        self.failUnless(isinstance(camera.driver, apps.cam.drivers.axis.AxisDriver))

    def test_interfaces_instantiation(self):
        camera_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        camera = Camera(type=camera_type)
        self.failUnless(isinstance(camera.driver.stream, apps.cam.drivers.axis.AxisStreamInterface))
        self.failUnless(isinstance(camera.driver.control, apps.cam.drivers.axis.AxisControlInterface))

    def test_stream_interface(self):
        camera_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        camera = Camera(type=camera_type)
        stream_interface = camera.driver.stream
        for method in (
            'check',
            'enable',
            'disable',
            ):
            self.failUnless(hasattr(stream_interface, method),
                            'stream interface has not method %s' % method)

            self.failUnless(callable(getattr(stream_interface, method)),
                            'stream interface method %s is not callable' % method)




    def test_control_interface(self):
        camera_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        camera = Camera(type=camera_type)
        control_interface = camera.driver.control
        for method in (
            'check',
            'zoom_in',
            'zoom_out',
            'move_up',
            'move_down',
            'move_left',
            'move_right',
            ):
            self.failUnless(hasattr(control_interface, method),
                            'control interface has not method %s' % method)

            self.failUnless(callable(getattr(control_interface, method)),
                            'control interface method %s is not callable' % method)


