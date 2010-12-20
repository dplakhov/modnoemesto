# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField, DateTimeField

from apps.utils.reflect import namedClass
from apps.billing.documents import AccessCamOrder
from django.core.urlresolvers import reverse
from django.conf import settings
from datetime import datetime
from apps.billing.constans import ACCESS_CAM_ORDER_STATUS


class CameraType(Document):
    name = StringField(max_length=255, unique=True)
    driver = StringField(max_length=255)
    is_controlled = BooleanField(default=False)

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
    SCREEN_URL_TPL = "/media/img/notfound/screen_%ix%i.png"

    name = StringField(max_length=255)

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

    operator = StringField(max_length=64)

    force_html5 = BooleanField()

    management_packet_tariff = ReferenceField('Tariff')
    management_time_tariff = ReferenceField('Tariff')

    view_packet_tariff = ReferenceField('Tariff')
    view_time_tariff = ReferenceField('Tariff')

    date_created = DateTimeField(default=datetime.now)

    @property
    def driver(self):
        return self.type.driver_class(self)

    def is_user_operator(self, user):
        return user.name == self.operator

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
                is_controlled=False,
                user=access_user,
                camera=self,
                end_date__gt=now,
            ).order_by('-end_date').only('end_date').first()
            if not order:
                return False
            time_left = order.end_date - now
            data = {}
            data['days'] = time_left.days
            data['hours'] = time_left.seconds / 3600
            data['minutes'] = (time_left.seconds % 3600) / 60
            data['seconds'] = time_left.seconds - data['minutes'] * 60
            for k, v in data.items():
                data[k] = "%2i" % v
            return data
        return True
    
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

    def get_screen_full(self):
        return reverse('cam:screen', args=[self.id, "%ix%i" % settings.SCREEN_SIZES[0]])

    def get_screen_normal(self):
        return reverse('cam:screen', args=[self.id, "%ix%i" % settings.SCREEN_SIZES[1]])

    def get_screen_mini(self):
        return reverse('cam:screen', args=[self.id, "%ix%i" % settings.SCREEN_SIZES[2]])

    @property
    def screen_full(self):
        return self.get_screen_full() if self.screen else Camera.SCREEN_URL_TPL % settings.SCREEN_SIZES[0]

    @property
    def screen_normal(self):
        return self.get_screen_normal() if self.screen else Camera.SCREEN_URL_TPL % settings.SCREEN_SIZES[1]

    @property
    def screen_mini(self):
        return self.get_screen_mini() if self.screen else Camera.SCREEN_URL_TPL % settings.SCREEN_SIZES[2]


class CameraBookmarks(Document):
    user = ReferenceField('User', unique=True)
    cameras = ListField(ReferenceField('Camera'))
