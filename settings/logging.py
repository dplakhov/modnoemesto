# -*- coding: utf-8 -*-

import django

if django.VERSION[1] < 3:
    LOGGING_CONFIG = 'apps.logging_patch.log.dictConfig'
    _adminEmailHandler = 'apps.logging_patch.log.AdminEmailHandler'
    _nullHandler = 'apps.logging_patch.log.NullHandler'
else:
    #for django version > 1.3.0
    LOGGING_CONFIG = 'django.utils.log.dictConfig'
    _adminEmailHandler = 'django.utils.log.AdminEmailHandler'
    _nullHandler = 'django.utils.log.NullHandler'

# end logging patches for django 1.2 series


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
            'level': 'DEBUG',
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
        'celery': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'root': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'multiprocessing': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'email': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'test_mongo_logger': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },

        'server_api': {
            'handlers': ['mongo'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

