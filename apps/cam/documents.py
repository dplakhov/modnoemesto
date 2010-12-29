# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from mongoengine import Q

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField, DateTimeField

from apps.utils.reflect import namedClass
from apps.billing.documents import AccessCamOrder
from datetime import datetime


class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    driver = StringField(max_length=255)
    is_controlled = BooleanField(default=False)
    is_default = BooleanField(default=False)

    @property
    def driver_class(self):
        return namedClass(self.driver)

    def get_option_value(self):
        return '%s.%s' % (self.id, 1 if self.is_controlled else 0)

    def get_option_label(self):
        return '%s %s' % (self.name,
                          _('(managed)') if self.is_controlled else _('(unmanaged)'))


class Camera(Document):
    TARIFF_FIELDS = ( 'management_packet_tariff',
                      'management_time_tariff',
                      'view_packet_tariff',
                      'view_time_tariff',
                  )

    name = StringField(max_length=255, default=unicode(_('New camera')))

    owner = ReferenceField('User')
    type = ReferenceField('CameraType')
    screen = ReferenceField('File')

    stream_name = StringField(max_length=255)

    camera_management_host = StringField(max_length=255)
    camera_management_username = StringField(max_length=64)
    camera_management_password = StringField(max_length=64)

    is_view_enabled = BooleanField()
    is_view_public = BooleanField(default=True)
    is_view_paid = BooleanField(default=False)

    is_management_enabled = BooleanField()
    is_management_public = BooleanField(default=True)
    is_management_paid = BooleanField(default=False)

    is_managed = BooleanField()

    operator = ReferenceField('User')

    force_html5 = BooleanField()

    management_packet_tariff = ReferenceField('Tariff')
    management_time_tariff = ReferenceField('Tariff')

    view_packet_tariff = ReferenceField('Tariff')
    view_time_tariff = ReferenceField('Tariff')

    date_created = DateTimeField(default=datetime.now)

    @property
    def driver(self):
        return self.type.driver_class(self)

    def can_show(self, owner_user, access_user):
        if not self.is_view_enabled:
            return False
        if not self.is_view_public:
            is_friend = access_user.is_authenticated() and \
                        access_user.friends.contains(owner_user)
            if not is_friend:
                return False
        if self.is_view_paid:
            if not owner_user.is_authenticated():
                return False
            now = datetime.now()
            order = AccessCamOrder.objects(
                user=access_user,
                camera=self,
            ).order_by('-create_on').first()
            if not order or order.end_date < now:
                return False
            data = {}
            if order.tariff.is_packet:
                time_left = order.end_date - now
                seconds = time_left.seconds
                data['days'] = time_left.days
            else:
                seconds = order.get_time_left()
            data['hours'] = seconds / 3600
            seconds -= data['hours'] * 3600
            data['minutes'] = seconds / 60
            data['seconds'] = seconds - data['minutes'] * 60
            return data
        return True

    def can_manage(self, owner_user, access_user):
        if not self.is_management_enabled:
            return False
        if not self.is_management_public:
            is_friend = access_user.is_authenticated() and \
                        access_user.friends.contains(owner_user)
            if not is_friend:
                return False
        if self.is_management_paid:
            if not owner_user.is_authenticated():
                return False
            now = datetime.now()
            orders = list(AccessCamOrder.objects(
                Q(end_date__gt=now) | Q(end_date__exists=True),
                is_controlled=True,
                camera=self,
            ).order_by('create_on'))
            if not orders:
                if self.operator:
                    self.operator = None
                    self.save()
                return False
            if orders[0].user == access_user:
                self.operator = access_user
                self.save()
            return orders
        return True

    def check_operator(self, order):
        if order.is_controlled and order.can_access():
            self.operator = order.user
            self.save()

    def save(self, *args, **kwargs):
        self.is_managed = self.type.is_controlled
        super(Camera, self).save()

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
