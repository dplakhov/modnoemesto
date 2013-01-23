
from datetime import datetime
from mongoengine import *
from mongoengine import connection


class Note(Document):
    title = StringField(max_length=128, required=True)
    text = StringField(required=True)
    author = ReferenceField('User')
    timestamp = DateTimeField()
    is_public = BooleanField(default=True)

    meta = {
        'indexes': ['-timestamp', 'author'],
        'ordering': ['-timestamp'],
    }


    def __init__(self, *args, **kwargs):
        super(Note, self).__init__(*args, **kwargs)
        self.timestamp = self.timestamp or datetime.now()