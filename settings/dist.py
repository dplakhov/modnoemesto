# -*- coding: utf-8 -*-

import os
import sys
from datetime import timedelta

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.path.pardir))

def rel(x):
    return os.path.join(PROJECT_ROOT, x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),
    },

    'billing': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': rel('billing.db'),
    },
}

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:', #rel('default.db'),

        },

        'billing': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },

    }
    TEST_RUNNER = 'djcelery.contrib.test_runner.run_tests'

MONGO_HOST = '127.0.0.1'

DATABASE_ROUTERS = [ 'db_routers.BillingRouter', ]

TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

USE_I18N = True

USE_L10N = True


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

LOGIN_URL = '/login/'

LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^in_dev/$',
    r'^static',
    r'^start/$',
    r'^stop/$',
    r'^pay/pskb/$',
    r'^pay/robokassa/',
    r'^register/$',
    r'^file/',
    r'^avatar/',
    r'^cam/screen/',
    r'^groups/.*/members\.(xml|txt)',
    r'^groups/can_manage/',
    r'^activation/',
    r'^media/',
    r'^invite/[a-f0-9]{24}/$',
    r'^lostpassword/',
    r'^resendactivationcode/',
    r'^recoverypassword/',
    ur'^ЕГГОГ',
    r'^captcha/',
    r'^robots.txt$',
    r'^billing/camera/notify/',
    r'^srv/',
    r'^api/',
    r'^theme/',
)

# Make this unique, and don't share it with anybody.
if not hasattr(globals(), 'SECRET_KEY'):
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'settings/secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            CHAR_SET = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            SECRET_KEY = ''.join([choice(CHAR_SET) for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            raise Exception('Please create a %s file with random characters to '
                'generate your secret key!' % SECRET_FILE)


TEMPLATE_LOADERS = (
    'apps.themes.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'apps.social.context_processors.site_domain',
    'apps.video_call.context_processors.call_settings',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.LoginRequiredMiddleware',
    'apps.social.middleware.SetLastAccessMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'apps.cam.middleware.PlaceBoxMiddleware',
    'apps.news.middleware.LastNewsMiddleware',
)


INSTALLED_APPS = (
    'django.contrib.sessions',
    'djcelery',
    'pytils',
    'apps.robokassa',
    'apps.social',
    'apps.media',
    'apps.cam',
    'apps.notes',
    'apps.user_messages',
    'apps.media_library',
    'apps.billing',
    'apps.groups',
    'apps.friends',
    'apps.logging',
    'apps.news',
    'apps.admin_blog',
    'apps.chat',
    'apps.server_api',
    'apps.async_email',
    'apps.invite',
    'apps.themes',
)



AUTHENTICATION_BACKENDS = (
    'apps.social.auth.MongoEngineBackend',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

FORCE_SCRIPT_NAME = ''

SEND_EMAILS = True

ROOT_URLCONF = 'urls'

#######################################################
MONGO_DATABASE = 'social'


TEMPLATE_DIRS = (
    rel('sites/modnoemesto/templates/')
)

LOCALE_PATHS = (
    rel('sites/modnoemesto/templates/locale'),
)

MEDIA_ROOT = rel('sites/modnoemesto/media/')

SITE_DOMAIN = 'modnoemesto.ru' # no slashes here, please
SERVER_EMAIL = 'modnoemesto.ru <modnoemesto@modnoemesto.ru>'

#######################################################


MAX_USER_MESSAGES_COUNT = 500

LIBRARY_IMAGES_PER_PAGE = 2

MESSAGES_ON_PAGE = 10

GROUP_USERS_ON_PAGE = 28

TIME_IS_ONLINE = timedelta(minutes=5)
LAST_ACCESS_UPDATE_INTERVAL = timedelta(minutes=5)

ALLOWED_SERVER_IPS = (
    '127.0.0.1',
    '213.170.69.53',

    '188.93.20.18',
    '188.93.20.19',
    '188.93.21.227',
)

GROUP_DESCRIPTION_MAX_LENGTH = 1200

VIDEO_CALL_INTERVAL_UPDATE = 5 # sec.


from .billing import *
from .captcha import *
from .celery_config import *
from .chat import *
from .logging import *
from .media import *
from .pagination import *
from .redis import *
