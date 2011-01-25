# -*- coding: utf-8 -*-

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
