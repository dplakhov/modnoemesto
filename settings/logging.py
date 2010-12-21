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
            'class': 'apps.logging_patch.log.MongoHander',
        },
        
        'mongo_info': {
            'level': 'INFO',
            'class': 'apps.logging_patch.log.MongoHander',
        },
        'mongo_debug': {
            'level': 'DEBUG',
            'class': 'apps.logging_patch.log.MongoHander',
        },
        'mongo_warning': {
            'level': 'WARNING',
            'class': 'apps.logging_patch.log.MongoHander',
        },
        'mongo_error': {
            'level': 'ERROR',
            'class': 'apps.logging_patch.log.MongoHander',
        },
        'mongo_critical': {
            'level': 'CRITICAL',
            'class': 'apps.logging_patch.log.MongoHander',
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
        'myproject.custom': {
            'handlers': ['console'],
            'level': 'INFO',
            #'filters': ['special']
        },
        'test_logger_info': {
            'handlers': ['mongo_info'],
            'level': 'INFO',
        },
        'test_logger_debug': {
            'handlers': ['mongo_debug'],
            'level': 'DEBUG',
        },
        'test_logger_warning': {
            'handlers': ['mongo_warning'],
            'level': 'WARNING',
        },
        'test_logger_error': {
            'handlers': ['mongo_error'],
            'level': 'ERROR',
        },
        'test_logger_critical': {
            'handlers': ['mongo_critical'],
            'level': 'CRITICAL',
        },
 
    }
}

