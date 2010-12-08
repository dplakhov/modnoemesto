# -*- coding: utf-8 -*-

DEBUG = TEMPLATE_DEBUG = False


DATABASES['billing'] = {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'billing',
            'USER': 'root',
            'PASSWORD': 'Eekeilt0',
            'HOST': '10.10.10.7',
        }


