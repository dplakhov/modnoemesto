# -*- coding: utf-8 -*-
from celery.decorators import task
from .documents import News


@task()
def send_notification(id):
    pass
