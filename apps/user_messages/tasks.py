# -*- coding: utf-8 -*-

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import timedelta

@task()
def message_store_set_readed(message_id, timestamp=None):
    from .documents import Message
    from apps.social.documents import Account
    message = Message.objects.get(id=message_id)
    message.store_set_readed(timestamp)

@task()
def message_store_sender_delete(message_id, timestamp=None):
    from .documents import Message
    from apps.social.documents import Account
    message = Message.objects.get(id=message_id)
    message.store_sender_delete(timestamp)

@task()
def message_store_recipient_delete(message_id, timestamp=None):
    from .documents import Message
    from apps.social.documents import Account
    message = Message.objects.get(id=message_id)
    message.store_recipient_delete(timestamp)

@periodic_task(run_every=timedelta(days=1))
def clean_deleted_messages():
    return
    # TODO
    from .documents import Message
    print Message.objects.find()