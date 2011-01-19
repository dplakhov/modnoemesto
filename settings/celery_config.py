TASKS_ENABLED = dict(
    AVATAR_RESIZE=1,
    MESSAGE_STORE_READED=1,
    MESSAGE_DELETE=1,
    CAM_SCREEN_RESIZE=0,
    GROUP_PHOTO_RESIZE=0,
)

TASKS_ENABLED = {}

CELERY_IMPORTS = ('apps.async_email.tasks',)

# celery email
#CELERY_ALWAYS_EAGER = True
#CELERY_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
#EMAIL_BACKEND = 'apps.async_email.backends.CeleryEmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


# for tests
CELERY_EMAIL_TASK_CONFIG = {
    'queue' : 'django_email',
    'delivery_mode' : 1, # non persistent
    'rate_limit' : '50/m', # 50 emails per minute
}

