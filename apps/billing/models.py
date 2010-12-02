# -*- coding: utf-8 -*-

from django.db.models.base import Model
from django.db import models
from datetime import datetime
from apps.social.documents import User


class UserOrder(Model):
    user_id = models.CharField(max_length=24)
    amount = models.FloatField(null=True)
    term = models.IntegerField(null=True)
    trans = models.IntegerField(null=True)
    timestamp = models.DateTimeField(default=datetime.now)

    @property
    def user(self):
        if not hasattr(self,'_user'):
            self._user = User.objects(id=self.user_id).first()
        return self._user