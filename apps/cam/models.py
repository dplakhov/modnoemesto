# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField


class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    code = StringField(max_length=255)

class Camera(Document):
    name = StringField(max_length=255)
    owner = ReferenceField('Account')
    type = ReferenceField('CameraType')
    ip = StringField(max_length=15)
    username = StringField(max_length=64)
    password = StringField(max_length=64)
    enabled = BooleanField()
