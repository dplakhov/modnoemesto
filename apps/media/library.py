# -*- coding: utf-8 -*-

from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import DateTimeField
from mongoengine import ListField

from .files import ImageFile, VideoFile
from mongoengine.fields import GenericReferenceField, BooleanField


def _get_common(cls):
    try:
        return cls.objects.get(is_common=True)
    except Exception, e:
        obj = cls(is_common=True)
        obj.save()
        return obj

def _save(self, *args, **kwargs):
    if self.is_common:
        if not self.id and self.__class__.objects(is_common=True).count():
            raise RuntimeError()

    if not self.save_allowed:
        raise RuntimeError()

    return super(self.__class__, self).save(*args, **kwargs)



class ImageLibrary(Document):
    author = ReferenceField('Account', required=False)
    items = ListField(ReferenceField(ImageFile))
    is_common = BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        self.save_allowed = True
        super(self.__class__, self).__init__(*args, **kwargs)

    @classmethod
    def get_common(cls):
        return _get_common(cls)

    def add(self, item):
        self.items.append(item)
        self.save_allowed = False
        self.__class__.objects(id=self.id).update_one(push__items=item)

    def save(self, *args, **kwargs):
        return _save(self, *args, **kwargs)



class VideoLibrary(Document):
    author = ReferenceField('Account', required=False)
    items = ListField(ReferenceField(VideoFile))
    is_common = BooleanField(default=False)

    @classmethod
    def get_common(cls):
        return _get_common(cls)

    def save(self, *args, **kwargs):
        return _save(self, *args, **kwargs)


