
CELERY_RESULT_BACKEND = "mongodb"

CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": "celery",
    "taskmeta_collection": "taskmeta",
}

TASKS_ENABLED = dict(
    AVATAR_RESIZE = 1,
    MESSAGE_STORE_READED = 1,
    MESSAGE_DELETE = 1,
    CAM_SCREEN_RESIZE = 0,
    GROUP_PHOTO_RESIZE = 0,
)

TASKS_ENABLED = {}




# celery email
CELERY_ALWAYS_EAGER = True
CELERY_EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
# for tests
CELERY_EMAIL_TASK_CONFIG = {
    'queue' : 'django_email',
    'delivery_mode' : 1, # non persistent
    'rate_limit' : '50/m', # 50 emails per minute
}
