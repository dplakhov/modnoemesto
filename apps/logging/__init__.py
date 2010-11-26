# -*- coding: utf-8 -*-
import django
if django.VERSION[1] < 3:
    from .patch import *