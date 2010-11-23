# -*- coding: utf-8 -*-

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import timedelta

@task()
def message_store_set_readed(message_id, timestamp=None):
    from .documents import Message

    # needs for deserialization
    from apps.social.documents import Account

    message = Message.objects.get(id=message_id)
    message.store_set_readed(timestamp)