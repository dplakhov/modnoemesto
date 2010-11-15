# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField 


class CameraType(Document):
    name = StringField(max_length=255)


class Camera(Document):
    name = StringField(max_length=255)
    owner = ReferenceField('Account')
    type = ReferenceField('CameraType')