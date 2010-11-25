# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField, IntField, DateTimeField
from datetime import datetime, timedelta
from apps.billing.constans import ACCESS_CAM_ORDER_STATUS


class Tariff(Document):
    name = StringField(required=True, unique=True, max_length=255)
    description = StringField()
    cost = IntField(required=True)
    duration = IntField(required=True)
    is_controlled = BooleanField(default=False)


class AccessCamOrder(Document):
    is_controlled = BooleanField(default=False)
    tariff = ReferenceField('Tariff')
    # in minutes
    duration = IntField(required=True)
    camera = ReferenceField('Camera')
    user = ReferenceField('User')
    begin_date = DateTimeField()
    end_date = DateTimeField()
    create_on = DateTimeField(default=datetime.now)

    def set_access_period(self, tariff=None):
        if tariff is None:
            tariff = self.tariff
        self.begin_date = datetime.now()
        duration_complete = self.duration * tariff.duration
        self.end_date = self.begin_date + timedelta(minutes=duration_complete)

    def can_access(self):
        return self.status == ACCESS_CAM_ORDER_STATUS.ACTIVE

    @property
    def status(self):
        if self.begin_date is None or self.end_date is None:
            return ACCESS_CAM_ORDER_STATUS.WAIT
        dnow = datetime.now()
        if self.begin_date <= dnow:
            if dnow <= self.end_date:
                return ACCESS_CAM_ORDER_STATUS.ACTIVE
            return ACCESS_CAM_ORDER_STATUS.COMPLETE
        return ACCESS_CAM_ORDER_STATUS.WAIT