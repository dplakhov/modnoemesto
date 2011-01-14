# -*- coding: utf-8 -*-

import logging
from django.conf import settings
from django.core.mail import get_connection
from celery.decorators import task


CONFIG = getattr(settings, 'CELERY_EMAIL_TASK_CONFIG', {})
BACKEND = getattr(settings, 'CELERY_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')

@task()
def send_email(message):
    conn = get_connection(backend=BACKEND)

    try:
        conn.send_messages([message])
        logging.debug("Successfully sent email message")
    except:
        logging.error("Error to send email")


from celery.registry import tasks
tasks.register(send_email)

#for key, val in CONFIG.iteritems():
#    setattr(send_email, key, val)

