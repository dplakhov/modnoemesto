# -*- coding: utf-8 -*-

import os

def rel(x):
    return os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__),
                os.path.pardir)),
            x)

MONGO_DATABASE = 'mestovstrechi'
CACHE_MIDDLEWARE_KEY_PREFIX = 'mv'

TEMPLATE_DIRS = (
    rel('sites/mestovstrechi/templates/'),
    rel('sites/modnoemesto/templates/')
)

LOCALE_PATHS = (
    rel('sites/mestovstrechi/templates/locale'),
    rel('sites/modnoemesto/templates/locale')
)

MEDIA_ROOT = rel('sites/mestovstrechi/media/')

SITE_DOMAIN = 'mestovstrechi.piter.tv' # no slashes here, please
SERVER_EMAIL = 'mestovstrechi.piter.tv <mestovstrechi@mestovstrechi.piter.tv>'


DEBUG = TEMPLATE_DEBUG = False

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
       'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),
    },
}


CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

REDIS_DATABASES = dict(
    streamed_users=dict(host='127.0.0.1', port=6379),

)

EMAIL_HOST = 'mail1.modnoemesto.ru'
EMAIL_HOST = '127.0.0.1'

ROBOKASSA_TEST_MODE = False

CELERYD_LOG_TO_CONSOLE = False
