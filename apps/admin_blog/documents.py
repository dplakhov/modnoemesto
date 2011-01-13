# -*- coding: utf-8 -*-

from datetime import datetime
from mongoengine import Document

from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import StringField

class AdminBlog(Document):
    title = StringField(max_length=128, required=True)
    text = StringField(required=True)
    author = ReferenceField('User')
    ctime = DateTimeField(default=datetime.now)
