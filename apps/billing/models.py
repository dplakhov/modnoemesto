# -*- coding: utf-8 -*-

from django.db.models.base import Model
from django.db import models
from datetime import datetime
from documents import *


class UserOrder(Model):
    user = models.CharField(max_length=24)
    amount = models.FloatField(null=True)
    term = models.IntegerField(null=True)
    trans = models.IntegerField(null=True)
    timestamp = models.DateTimeField(default=datetime.now)