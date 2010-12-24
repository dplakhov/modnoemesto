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

MONGO_DATABASE = 'social'
MONGO_HOST = '127.0.0.1'

DATABASE_ROUTERS = [ 'db_routers.BillingRouter', ]

TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = (
    rel('templates/locale'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = rel('media/')

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
    r'^register/$',
    r'^file/',
    r'^avatar/',
    r'^cam/screen/',
    r'^activation/',
    r'^media/',
    r'^invite/',
    r'^lostpassword/',
    r'^resendactivationcode/',
    r'^recoverypassword/',
    ur'^ЕГГОГ',
    r'^captcha/',
    r'^robots.txt$',
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


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'apps.social.context_processors.site_domain',

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

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Don't forget to use absolute paths, not relative paths.
    rel('templates/')
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.admin',
    #'mongoengine.django.auth',
    'djcelery',
    'pytils',
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
)


AUTHENTICATION_BACKENDS = (
    'apps.social.auth.MongoEngineBackend',
)

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

FORCE_SCRIPT_NAME = ''

SEND_EMAILS = True

SITE_DOMAIN = 'modnoemesto.ru' # no slashes here, please

ROBOT_EMAIL_ADDRESS = 'modnoemesto.ru <modnoemesto@modnoemesto.ru>'

SERVER_EMAIL = ROBOT_EMAIL_ADDRESS

AVATAR_SIZES = (
    (200, 200),
    (60, 60),
    (47, 47),
)

SCREEN_SIZES = (
    (515, 330),
    (170, 109),
    (80, 51),
)

MAX_USER_MESSAGES_COUNT = 500

LIBRARY_IMAGES_PER_PAGE = 2

TIME_IS_ONLINE = timedelta(minutes=5)
LAST_ACCESS_UPDATE_INTERVAL = timedelta(minutes=5)


from .logging import *
from .billing import *
from .celery import *
from .captcha import *
from .chat import *
