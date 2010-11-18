# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField
from reflect import namedClass

class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    driver = StringField(max_length=255)

    @property
    def driver_class(self):
        return namedClass(self.driver)


class Camera(Document):
    name = StringField(max_length=255)
    owner = ReferenceField('Account')
    type = ReferenceField('CameraType')
    host = StringField(max_length=15)
    username = StringField(max_length=64)
    password = StringField(max_length=64)
    enabled = BooleanField()
    public = BooleanField(default=True)
    free = BooleanField(default=True)
    operator = StringField(max_length=64)

    @property
    def driver(self):
        return self.type.driver_class(self)
