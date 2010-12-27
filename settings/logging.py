# -*- coding: utf-8 -*-
import django

# patches for django 1.2 series
if django.VERSION[1] < 3:
    LOGGING_CONFIG = 'apps.logging_patch.log.dictConfig'
    _adminEmailHandler = 'apps.logging_patch.log.AdminEmailHandler'
    _nullHandler = 'apps.logging_patch.log.NullHandler'
else:
    #for django version > 1.3.0
    LOGGING_CONFIG = 'django.utils.log.dictConfig'
    _adminEmailHandler = 'django.utils.log.AdminEmailHandler'
    _nullHandler = 'django.utils.log.NullHandler'


LOGS_PER_PAGE = 50



LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    #'filters': {
     #    'special': {
     #        '()': 'project.logging.SpecialFilter',
     #       'foo': 'bar',
     #   }
    #},
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':_nullHandler,
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },

        'mail_admins': {
            'level': 'ERROR',
            'class': _adminEmailHandler,
            #'filters': ['special']
        }
        ,
        
        'mongo': {
            'level': 'INFO',
            'class': 'apps.logging.log.MongoHander',
        },
        
        'mongo_info': {
            'level': 'INFO',
            'class': 'apps.logging.log.MongoHander',
        },
        'mongo_debug': {
            'level': 'DEBUG',
            'class': 'apps.logging.log.MongoHander',
        },
        'mongo_warning': {
            'level': 'WARNING',
            'class': 'apps.logging.log.MongoHander',
        },
        'mongo_error': {
            'level': 'ERROR',
            'class': 'apps.logging.log.MongoHander',
        },
        'mongo_critical': {
            'level': 'CRITICAL',
            'class': 'apps.logging.log.MongoHander',
        },


        
    },
    'loggers': {
        'django': {
            'handlers':['console', 'mail_admins', 'mongo'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'test_logger_info': {
            'handlers': ['mongo_info'],
            'level': 'INFO',
            'propagate': True,
        },
        'test_logger_debug': {
            'handlers': ['mongo_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'test_logger_warning': {
            'handlers': ['mongo_warning'],
            'level': 'WARNING',
            'propagate': True,
        },
        'test_logger_error': {
            'handlers': ['mongo_error'],
            'level': 'ERROR',
            'propagate': True,
        },
        'test_logger_critical': {
            'handlers': ['mongo_critical'],
            'level': 'CRITICAL',
            'propagate': True,
        },
 
    }
}

import importlib
import django

# patches for django 1.2 series
if django.VERSION[1] < 3:
    if LOGGING_CONFIG:
        # First find the logging configuration function ...
        logging_config_path, logging_config_func_name = LOGGING_CONFIG.rsplit('.', 1)
        logging_config_module = importlib.import_module(logging_config_path)
        logging_config_func = getattr(logging_config_module, logging_config_func_name)

        # ... then invoke it with the logging settings
        logging_config_func(LOGGING)

