# -*- coding: utf-8 -*-

from celery.decorators import task, periodic_task
from celery.task.schedules import crontab
from datetime import timedelta
