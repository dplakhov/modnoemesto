# -*- coding: utf-8 -*-


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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'billing',
        'USER': 'billing',
        'PASSWORD': 'akonEmjad2',
        'HOST': '127.0.0.1',
    },
}


CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

REDIS_DATABASES = dict(
    streamed_users=dict(host='127.0.0.1', port=6379),

)

ROBOKASSA_TEST_MODE = False

CELERYD_LOG_TO_CONSOLE = False
