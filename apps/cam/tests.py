# -*- coding: utf-8 -*-
from django.test import TestCase

import apps.cam.drivers.axis
from models import CameraType

class CameraDriverTest(TestCase):
    def test_driver_loading(self):
        cam_type = CameraType(name='axis', driver='apps.cam.drivers.axis.AxisDriver')
        self.failUnlessEqual(apps.cam.drivers.axis.AxisDriver,
                             cam_type.driver_class
                             )

