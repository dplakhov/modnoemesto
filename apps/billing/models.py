# -*- coding: utf-8 -*-

from django.db.models.base import Model
from django.db import models
from datetime import datetime
from apps.social.documents import User
from apps.utils.decorators import cached_property


class UserOrder(Model):
    user_id = models.CharField(max_length=24)
    amount = models.FloatField(null=True)
    term = models.IntegerField(null=True)
    trans = models.IntegerField(null=True)
    timestamp = models.DateTimeField(default=datetime.now)

    @cached_property
    def user(self):
        return User.objects(id=self.user_id).first()
