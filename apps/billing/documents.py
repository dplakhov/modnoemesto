# -*- coding: utf-8 -*-

from mongoengine import Document, ReferenceField, StringField, IntField, FloatField, DateTimeField, BooleanField
from datetime import datetime, timedelta
from apps.billing.constans import ACCESS_CAM_ORDER_STATUS
from mongoengine.queryset import Q


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
    duration = FloatField(default=0.0) # in seconds
    count_packets = IntField()
    camera = ReferenceField('Camera')
    user = ReferenceField('User')
    begin_date = DateTimeField()
    end_date = DateTimeField()
    cost = FloatField()
    create_on = DateTimeField(default=datetime.now)


    @property
    def is_packet(self):
        return self.count_packets is not None

    @property
    def status(self):
        if self.begin_date is None:
            return ACCESS_CAM_ORDER_STATUS.WAIT
        now = datetime.now()
        if self.begin_date <= now:
            if self.end_date is None or now < self.end_date:
                return ACCESS_CAM_ORDER_STATUS.ACTIVE
            return ACCESS_CAM_ORDER_STATUS.COMPLETE
        return ACCESS_CAM_ORDER_STATUS.WAIT


    @classmethod
    def create_packet_type(cls, user, camera, tariff, count_packets):
        assert tariff.is_packet
        order = cls(user=user, camera=camera, tariff=tariff)
        order.count_packets = count_packets
        order.cost = tariff.cost * order.count_packets
        order.duration = order.count_packets * tariff.duration
        order.set_access_period()
        order.save()
        return order

    @classmethod
    def create_time_type(cls, user, camera, tariff):
        assert not tariff.is_packet
        order = cls(user=user, camera=camera, tariff=tariff)
        order.set_access_period()
        order.save()
        return order


    def __init__(self, *args, **kwargs):
        super(AccessCamOrder, self).__init__(*args, **kwargs)
        if self.is_controlled is None:
            self.is_controlled = self.tariff.is_controlled

    def save(self, *args, **kwargs):
        if self.id is None:
            is_new = True
        super(AccessCamOrder, self).save(*args, **kwargs)
        if self.is_packet and is_new:
            self.user.cash -= self.cost
            self.user.save()


    def set_end_date(self):
        self.end_date = self.begin_date + timedelta(seconds=self.duration)

    def set_access_period(self):
        q_data = dict(camera=self.camera,
                      is_controlled=self.is_controlled)
        if not self.is_controlled:
            q_data.update(dict(user=self.user))
        last_order = AccessCamOrder.objects(**q_data).order_by('-create_on').only('end_date').first()

        now = datetime.now()
        if last_order:
            if last_order.end_date:
                self.begin_date = last_order.end_date if last_order.end_date > now else now
            elif self.is_controlled:
                # find time user order
                q_data.update(dict(user=self.user,
                                   end_date__exists=False,
                                   count_packets__exists=False, # is not packet
                                   ))
                if AccessCamOrder.objects(**q_data).count() > 0:
                    raise AccessCamOrder.CanNotAddOrder()
            else:
                raise AccessCamOrder.CanNotAddOrder()
        else: # first order
            self.begin_date = now
        if self.begin_date and self.is_packet:
            self.set_end_date()

    def set_time_at_end(self):
        if self.end_date is not None or self.count_packets is not None:
            return False
        self.end_date = self.begin_date + timedelta(seconds=self.duration)

        if self.is_controlled:
            orders = AccessCamOrder.objects(camera=self.camera,
                                            is_controlled=self.is_controlled,
                                            create_on__gt=self.create_on).order_by('create_on'),all()
            if orders:
                last_end_date = self.end_date
                for order in orders:
                    if order.count_packets is not None:
                        break
                    order.begin_date = last_end_date + timedelta(seconds=1)
                    order.set_end_date()
                    order.save()
                    last_end_date = order.end_date
                if self.is_controlled:
                    self.camera.operator = orders[0].user
            else:
                self.camera.operator = None
            self.camera.save()

    def can_access(self):
        return self.status == ACCESS_CAM_ORDER_STATUS.ACTIVE

    def get_time_left(self, user_cash=None):
        user_cash = user_cash or self.user.cash
        return int(user_cash/self.tariff.cost)


    class CanNotAddOrder(Exception):
        pass