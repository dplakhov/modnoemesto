# -*- coding: utf-8 -*-
import django

# patches for django 1.2 series

if django.VERSION[1] < 3:
    LOGGING_CONFIG = 'apps.logging.patch.log.dictConfig'
    _adminEmailHandler = 'apps.logging.patch.log.AdminEmailHandler'
    _nullHandler = 'apps.logging.patch.log.NullHandler'
else:
    #for django version > 1.3.0
    LOGGING_CONFIG = 'django.utils.log.dictConfig'
    _adminEmailHandler = 'django.utils.log.AdminEmailHandler'
    _nullHandler = 'django.utils.log.NullHandler',

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
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'myproject.custom': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
            #'filters': ['special']
        }
    }
}

