# -*- coding: utf-8 -*-

from django.db.models.base import Model
from django.db import models
from datetime import datetime


class UserOrder(Model):
    user = models.CharField(max_length=24)
    total = models.IntegerField()
    is_payed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=datetime.now)