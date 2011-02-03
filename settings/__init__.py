import sys
import mongoengine






from dist import *
try:
    from local import *
except ImportError:
    pass



# logging patches for django 1.2 series
import django
import importlib

if django.VERSION[1] < 3:
    if LOGGING_CONFIG:
        # First find the logging configuration function ...
        logging_config_path, logging_config_func_name = LOGGING_CONFIG.rsplit('.', 1)
        logging_config_module = importlib.import_module(logging_config_path)
        logging_config_func = getattr(logging_config_module, logging_config_func_name)

        # ... then invoke it with the logging settings
        logging_config_func(LOGGING)

# end logging patches for django 1.2 series


# celery logging patches

if not CELERYD_LOG_TO_CONSOLE:
    import celery.log
    celery.log._setup = True
# end  celery logging patches



mongoengine.connect(MONGO_DATABASE +
                    ('_test' if 'test' in sys.argv else ''),
                    host=MONGO_HOST
    )

import djcelery
djcelery.setup_loader()