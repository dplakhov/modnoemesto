# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField
from reflect import namedClass
from apps.billing.documents import AccessCamOrder

class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    driver = StringField(max_length=255)
    is_controlled = BooleanField(default=False)

    @property
    def driver_class(self):
        return namedClass(self.driver)


class Camera(Document):
    name = StringField(max_length=255)
    owner = ReferenceField('Account')
    type = ReferenceField('CameraType')
    host = StringField(max_length=255)
    username = StringField(max_length=64)
    password = StringField(max_length=64)
    enabled = BooleanField()
    public = BooleanField(default=True)
    paid = BooleanField(default=False)
    operator = StringField(max_length=64)
    tariffs = ListField(ReferenceField('Tariff'))

    @property
    def driver(self):
        return self.type.driver_class(self)

    def is_user_operator(self, user):
        return user.name == self.operator

    def can_show(self, user):
        if user.is_superuser:
            return True
        if not (self.public or user.is_friend):
            return False
        if self.paid:
            if not user.is_authenticated():
                return False
            order = AccessCamOrder.objects(
                user=user,
                camera=self,
            ).order_by('-create_on').first()
            if order is None or not order.can_access():
                return False
        return True