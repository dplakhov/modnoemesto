# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField, IntField, DateTimeField
from datetime import datetime


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
    status = StringField(max_length=10)
    camera = ReferenceField('Camera')
    user = ReferenceField('User')
    init_on = DateTimeField()
    create_on = DateTimeField(default=datetime.now)