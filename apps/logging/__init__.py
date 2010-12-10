# -*- coding: utf-8 -*-
import importlib
import django
from django.conf import settings

# patches for django 1.2 series
if django.VERSION[1] < 3:
    if settings.LOGGING_CONFIG:
        # First find the logging configuration function ...
        logging_config_path, logging_config_func_name = settings.LOGGING_CONFIG.rsplit('.', 1)
        logging_config_module = importlib.import_module(logging_config_path)
        logging_config_func = getattr(logging_config_module, logging_config_func_name)

        # ... then invoke it with the logging settings
        logging_config_func(settings.LOGGING)