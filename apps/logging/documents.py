# -*- coding: utf-8 -*-

from mongoengine.document import Document
from mongoengine.fields import DateTimeField, StringField, IntField

from datetime import datetime

from django.utils.encoding import smart_unicode
from apps.utils.enum import Enumeration


class LogEntry(Document):
    date = DateTimeField(default=datetime.now)
    levelname = StringField()
    levelnum = IntField()
    message = StringField()
    pathname = StringField()
    logger_name = StringField()
    func = StringField()
    lineno = IntField()
    
    def __unicode__(self):
        return u"[date: %s, message: %s, levelname: %s]" % (
            smart_unicode(self.date),
            self.message,
            smart_unicode(self.levelname),
        )
        
    meta = {
        'ordering':[
            '-date',
        ],
        'max_documents': 1000
    }