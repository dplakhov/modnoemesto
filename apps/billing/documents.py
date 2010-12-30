# -*- coding: utf-8 -*-

from mongoengine import Document, ReferenceField, StringField, IntField, FloatField, DateTimeField, BooleanField
from datetime import datetime, timedelta
from apps.billing.constans import ACCESS_CAM_ORDER_STATUS


class Tariff(Document):
    name = StringField(required=True, unique=True, max_length=255)
    description = StringField()
    cost = FloatField(required=True)
    # in seconds
    duration = IntField(required=False)

    # тариф на управление
    is_controlled = BooleanField(default=False)

    # пакетный тариф
    is_packet = BooleanField()



    meta = {
        'ordering': [
            'name',
        ]
    }

    def save(self, *args, **kwargs):
        self.is_packet = bool(self.duration)
        return super(Tariff, self).save(*args, **kwargs)


    @classmethod
    def get_management_packet_tariff_list(cls):
        return cls.objects(is_controlled=True, is_packet=True)
    
    @classmethod
    def get_management_time_tariff_list(cls):
        return cls.objects(is_controlled=True, is_packet=False)
    
    @classmethod
    def get_view_packet_tariff_list(cls):
        return cls.objects(is_controlled=False, is_packet=True)

    @classmethod
    def get_view_time_tariff_list(cls):
        return cls.objects(is_controlled=False, is_packet=False)


class AccessCamOrder(Document):
    is_controlled = BooleanField(default=False)
    tariff = ReferenceField('Tariff')
    # in seconds
    duration = FloatField()
    count_packets = IntField()
    camera = ReferenceField('Camera')
    user = ReferenceField('User')
    begin_date = DateTimeField()
    end_date = DateTimeField()
    cost = FloatField()
    create_on = DateTimeField(default=datetime.now)

    def __init__(self, *args, **kwargs):
        super(AccessCamOrder, self).__init__(*args, **kwargs)
        self.is_controlled = self.tariff.is_controlled
        if self.tariff.is_packet:
            self.cost = self.tariff.cost * self.count_packets
            self.user.cash -= self.cost
            self.user.save()

    @property
    def is_packet(self):
        return self.tariff.is_packet

    @property
    def duration_complete(self):
        return self.count_packets * self.tariff.duration

    def set_end_date(self):
        self.end_date = self.begin_date + timedelta(seconds=self.duration_complete)

    def set_access_period(self, is_controlled):
        now = datetime.now()
        if is_controlled:
            last_order = AccessCamOrder.objects(camera=self.camera,
                                                is_controlled=is_controlled,
                                                end_date__gt=now)
        elif self.is_packet:
            last_order = AccessCamOrder.objects(user=self.user,
                                                camera=self.camera,
                                                is_controlled=is_controlled,
                                                end_date__gt=now)
        if self.is_packet:
            last_order = last_order.order_by('-end_date').only('end_date').first()
            self.begin_date = last_order and last_order.end_date or now
            self.set_end_date()
        else:
            if is_controlled:
                last_order = last_order.order_by('-create_on').only('end_date').first()
                self.begin_date = last_order and last_order.end_date or now
            else:
                self.begin_date = now

    def set_end_time(self):
        if self.end_date is not None:
            return False
        self.end_date = self.begin_date + timedelta(seconds=self.count_packets)
        if self.is_controlled:
            orders = AccessCamOrder.objects(camera=self.camera,
                                            is_controlled=self.is_controlled,
                                            create_on__gt=self.create_on).order_by('create_on'),all()
            if orders:
                last_end_date = self.end_date
                for order in orders:
                    order.begin_date = last_end_date + timedelta(seconds=1)
                    if not order.is_packet:
                        order.save()
                        break
                    order.set_end_date()
                    order.save()
                    last_end_date = order.end_date
                self.camera.operator = orders[0].user
            else:
                self.camera.operator = None
            self.camera.save()

    def can_access(self):
        return self.status == ACCESS_CAM_ORDER_STATUS.ACTIVE

    def get_time_left(self, user_cash=None):
        user_cash = user_cash or self.user.cash
        return int(user_cash/self.tariff.cost)

    @property
    def status(self):
        if self.begin_date is None or self.end_date is None:
            return ACCESS_CAM_ORDER_STATUS.WAIT
        dnow = datetime.now()
        if self.begin_date <= dnow:
            if dnow < self.end_date:
                return ACCESS_CAM_ORDER_STATUS.ACTIVE
            return ACCESS_CAM_ORDER_STATUS.COMPLETE
        return ACCESS_CAM_ORDER_STATUS.WAIT