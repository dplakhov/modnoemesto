# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField, IntField, DateTimeField


class Tariff(Document):
    name = StringField(required=True, unique=True, max_length=255)
    description = StringField()
    cost = IntField(required=True)
    duration = IntField(required=True)
    is_controlled = BooleanField(default=False)


class AccessCamOrder(Document):
    is_controlled = BooleanField(default=False)
    tariff = ReferenceField('Tariff')
    duration = IntField(required=True)
    status = IntField()
    tariff = ReferenceField('Camera')
    user = ReferenceField('User')
    timestamp = DateTimeField()