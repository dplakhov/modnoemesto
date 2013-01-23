# -*- coding: utf-8 -*-

DEBUG = TEMPLATE_DEBUG = 0

ADMINS = (
    ('dp', 'dmitri.plakhov@gmail.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),
    },

    'billing': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'billing_test',
        'USER': 'billing_test',
        'PASSWORD': 'akonEsdfsdfd2',
        'HOST': '127.0.0.1',
    },
}


#CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'apps.async_email.backends.CeleryEmailBackend'

VIDEO_PROXY_SERVER_URL = 'rtmp://109.234.158.4/cam3'
