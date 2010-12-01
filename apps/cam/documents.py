# -*- coding: utf-8 -*-

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField
from reflect import namedClass
from apps.billing.documents import AccessCamOrder

class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    driver = StringField(max_length=255)
    is_controlled = BooleanField(default=False)

    @property
    def driver_class(self):
        return namedClass(self.driver)


class Camera(Document):
    name = StringField(max_length=255)
    owner = ReferenceField('User')
    type = ReferenceField('CameraType')
    stream_name = StringField(max_length=255)
    host = StringField(max_length=255)
    username = StringField(max_length=64)
    password = StringField(max_length=64)
    managed = BooleanField()
    enabled = BooleanField()
    public = BooleanField(default=True)
    paid = BooleanField(default=False)
    operator = StringField(max_length=64)
    tariffs = ListField(ReferenceField('Tariff'))

    @property
    def driver(self):
        return self.type.driver_class(self)

    def is_user_operator(self, user):
        return user.name == self.operator

    def can_show(self, user):
        if user.is_superuser:
            return True
        if not (self.public or user.is_friend):
            return False
        if self.paid:
            if not user.is_authenticated():
                return False
            order = AccessCamOrder.objects(
                user=user,
                camera=self,
            ).order_by('-create_on').first()
            if order is None or not order.can_access():
                return False
        return True

    def bookmark_add(self, user):
        owner_camera = Camera.objects(owner=user).only('id').first()
        if not owner_camera or owner_camera != self:
            cam_bookmark, created = CameraBookmarks.objects.only('id').get_or_create(user=user,
                                                                          defaults={'user': user})
            CameraBookmarks.objects(id=cam_bookmark.id)\
                           .update_one(add_to_set__cameras=self)

    def bookmark_delete(self, user):
        cam_bookmark, created = CameraBookmarks.objects.only('id').get_or_create(user=user,
                                                                      defaults={'user': user})
        if not created:
            CameraBookmarks.objects(id=cam_bookmark.id)\
                           .update_one(pull__cameras=self)

    def can_bookmark_add(self, user):
        cam_bookmark, created = CameraBookmarks.objects.only('cameras').get_or_create(user=user,
                                                                      defaults={'user': user})
        if created:
            return True
        return self not in cam_bookmark.cameras



class CameraBookmarks(Document):
    user = ReferenceField('User', unique=True)
    cameras = ListField(ReferenceField('Camera'))