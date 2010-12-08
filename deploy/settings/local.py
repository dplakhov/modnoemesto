# -*- coding: utf-8 -*-

DEBUG = TEMPLATE_DEBUG = False

ADMINS = (
    ('tech', 'tech@web-mark.ru'),
    ('dgk', 'dgk@web-mark.ru'),
    ('elias', 'elias@web-mark.ru'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),
    },

    'billing': {
        #'ENGINE': 'django.db.backends.mysql',
        #'NAME': 'billing',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),

        'USER': 'root',
        'PASSWORD': 'Eekeilt0',
        'HOST': '10.10.10.7',
    },
}

REDIS_HOST = "10.10.10.11"
