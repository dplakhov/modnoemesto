# -*- coding: utf-8 -*-

from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField

from datetime import datetime

class LogEntry(Document):
    date = DateTimeField(default=datetime.now)
    message = StringField()
    
    
    meta = {
        'ordering':[
            '-date',
        ],
        'max_documents': 1000
    }