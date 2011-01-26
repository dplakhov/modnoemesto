# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from mongoengine import Q

from mongoengine import Document, StringField, ReferenceField, BooleanField, ListField, DateTimeField, IntField

from apps.utils.reflect import namedClass
from apps.billing.documents import AccessCamOrder
from datetime import datetime, timedelta


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


class CameraTag(Document):
    name = StringField(max_length=255, unique=True)
    is_private = BooleanField(default=False)
    count = IntField(default=0)

    meta = {
        'ordering': [
                'name',
        ]

    }

    @staticmethod
    def calc_count(new_tag_ids, old_tag_ids=[]):
        for old_tag in old_tag_ids:
            if old_tag in new_tag_ids:
                new_tag_ids.remove(old_tag)
            else:
                CameraTag.objects(id=old_tag).update_one(dec__count=1)
        for new_tag in new_tag_ids:
            CameraTag.objects(id=new_tag).update_one(inc__count=1)


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

    tags = ListField(ReferenceField('CameraTag'))

    view_count = IntField(default=0)


    @property
    def driver(self):
        return self.type.driver_class(self)

    def can_show(self, access_user, now):
        if self.owner == access_user:
            return True
        if not self.is_view_enabled:
            return False
        if not self.is_view_public:
            if not access_user.friends.contains(self.owner):
                return False
        if self.is_view_paid:
            if self.operator == access_user:
                return True
            order = AccessCamOrder.objects(
                user=access_user,
                camera=self,
            ).order_by('-create_on').first()
            if not order or order.end_date is not None and order.end_date < now:
                return False
        return True

    def get_show_info(self, access_user, now):
        if self.operator == access_user or self.owner == access_user:
            return None, None
        order = AccessCamOrder.objects(
            user=access_user,
            camera=self,
        ).order_by('-create_on').first()
        if order.tariff.is_packet:
            time_left = order.end_date - now
        else:
            time_left = timedelta(seconds=order.get_time_left())
        return time_left, order

    def can_manage(self, access_user, now):
        if self.owner == access_user:
            return True
        if not self.is_management_enabled:
            return False
        if not self.is_management_public:
            if not access_user.friends.contains(self.owner):
                return False
        if self.is_management_paid and self.operator == None:
            orders = AccessCamOrder.objects(
                Q(end_date__gt=now) | Q(end_date__exists=False),
                is_controlled=True,
                camera=self,
            ).order_by('create_on').count()
            return orders > 0
        return self.operator == access_user

    def get_manage_list(self, now):
        return list(AccessCamOrder.objects(
            Q(end_date__gt=now) | Q(end_date__exists=False),
            is_controlled=True,
            camera=self,
        ).order_by('create_on'))

    def billing(self, access_user):
        now = datetime.now()
        can_show = self.can_show(access_user, now)
        show_data = {}
        if can_show and self.is_view_paid:
            time_left, order = self.get_show_info(access_user, now)
            if time_left is not None:
                seconds = time_left.seconds
                show_data['days'] = time_left.days
                show_data['hours'] = seconds / 3600
                seconds -= show_data['hours'] * 3600
                show_data['minutes'] = seconds / 60
                show_data['seconds'] = seconds - show_data['minutes'] * 60
        else:
            order = None
        can_manage = self.can_manage(access_user, now)
        manage_list = self.get_manage_list(now)
        return {
            'can_show': can_show,
            'show_data': show_data,
            'can_manage': can_manage,
            'manage_list': manage_list,
            'order': order,
        }

    def check_operator(self, order):
        if order.is_controlled and order.can_access():
            self.operator = order.user
            self.save()

    def save(self, *args, **kwargs):
        self.is_managed = self.type.is_controlled
        super(Camera, self).save(*args, **kwargs)

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
