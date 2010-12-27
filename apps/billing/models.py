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


class UserId(Model):
    user_id = models.CharField(max_length=24, db_index=True, unique=True)

    @staticmethod
    def get_id_by_user(user):
        return UserId.objects.get_or_create(user_id=user.id)[0].id

    @staticmethod
    def get_user_by_id(id):
        try:
            user = UserId.objects.get(id=id)
        except UserId.DoesNotExist:
            return None
        return User.objects(id=user.user_id).first()
