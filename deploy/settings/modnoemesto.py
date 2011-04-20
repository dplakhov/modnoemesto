# -*- coding: utf-8 -*-


DEBUG = TEMPLATE_DEBUG = False

ADMINS = (
    ('tech', 'tech@web-mark.ru'),
    ('dgk', 'dgk@web-mark.ru'),
    ('elias', 'elias@web-mark.ru'),
    ('eugene', 'eugene@web-mark.ru'),
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
        'HOST': '10.10.10.7',
    },
}


CACHE_BACKEND = 'memcached://10.10.10.11:11211/'

REDIS_DATABASES = dict(
    streamed_users=dict(host='10.10.10.11', port=6379),

)

ROBOKASSA_TEST_MODE = False

CELERYD_LOG_TO_CONSOLE = False
