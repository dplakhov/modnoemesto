# -*- coding: utf-8 -*-

import logging

from django.core.mail import get_connection
from django.conf import settings
from celery.decorators import task


CONFIG = getattr(settings, 'CELERY_EMAIL_TASK_CONFIG', {})
BACKEND = getattr(settings, 'CELERY_EMAIL_BACKEND',
                  'django.core.mail.backends.smtp.EmailBackend')

@task()
def send_email_task(message, **kwargs):
    conn = get_connection(backend=BACKEND)

    logger = logging.get_logger(**kwargs)

    try:
        conn.send_messages([message])
        if settings.DEBUG:
            logger.debug("Successfully sent email message: %s" % (message.message().as_string(),))
    except:
        logger.error("Error to send email")


for key, val in CONFIG.iteritems():
    setattr(send_email_task, key, val)

