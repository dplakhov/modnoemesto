# -*- coding: utf-8 -*-

from django.conf import settings
from datetime import datetime
from apps.cam.documents import Camera
from django.contrib.auth import SESSION_KEY
from django.utils.importlib import import_module
from apps.social.documents import User


class CameraAccessor(object):

    class APIException(Exception):
        pass

    def __init__(self, request):
        # extract data from request
        if not request.GET:
            raise CameraAccessor.APIException("Bad params")
        status = request.GET.get('status', None)
        session_key = request.GET.get('session_key', None)
        camera_id = request.GET.get('camera_id', None)
        if not (status and session_key and camera_id):
            raise CameraAccessor.APIException("Bad params")
        extra_time = request.GET.get('time', None)
        if extra_time is None:
            return
        if not extra_time.isdigit():
            raise CameraAccessor.APIException("Time must by a digit")
        extra_time = int(extra_time)
        if extra_time > settings.TIME_INTERVAL_NOTIFY or extra_time < 0:
            raise CameraAccessor.APIException("Bad time interval")

        # extract data from session
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore(session_key)
        user_id = session.get(SESSION_KEY, None)
        if not user_id:
            raise CameraAccessor.APIException("Need user_id")
        user = User.objects(id=user_id).first()
        if not user:
            raise CameraAccessor.APIException("Bad user_id")
        camera = Camera.objects(id=camera_id).first()
        if not camera:
            raise CameraAccessor.APIException("Can`t found camera by camera_id")

        # select next action
        try:
            f = { 'connect': self._connect,
                  'next': self._next,
                  'disconnect': self._disconnect }[status]
        except KeyError:
            raise CameraAccessor.APIException("Bad status")

        # call next action
        time = f(user, camera, session, extra_time, datetime.now())

        # result
        self.status = 0
        self.time = time
        self.stream = camera.stream_name

    def _save_new_time(self, order, extra_time):
        if order.begin_date is None:
            raise CameraAccessor.APIException("Need connect")
        total_cost = order.tariff.cost * extra_time
        order.user.cash -= total_cost
        order.user.save()
        order.duration += extra_time

    def _complete_order(self, order):
        order.set_time_at_end()
        order.cost = order.tariff.cost * order.duration
        order.save()

    def _check_packet(self, time_left):
        time_next = time_left.days * 60 * 60 * 24 + time_left.seconds
        if time_next > settings.TIME_INTERVAL_NOTIFY:
            time_next = settings.TIME_INTERVAL_NOTIFY
        return time_next

    def _connect(self, user, camera, session, extra_time, now):
        can_show, can_show_info = camera.can_show(user, now)
        if not can_show:
            if can_show_info == 'not_paid':
                time_left = camera.get_trial_view_time(session)
                if time_left > 0:
                    time_next = time_left
                    if time_next > settings.TIME_INTERVAL_NOTIFY:
                        time_next = settings.TIME_INTERVAL_NOTIFY
                    return time_next
            self.status = 'OK'
            self.time = 0
            self.stream = camera.stream_name
            return 0
        if can_show_info in ['owner', 'free']:
            return settings.TIME_INTERVAL_NOTIFY
        time_left, order = camera.get_show_info(user, now)
        if order.is_packet:
            time_next = self._check_packet(time_left)
        else:
            if order.begin_date is not None:
                raise CameraAccessor.APIException("order.begin_date must by None")
            order.begin_date = datetime.now()
            time_next = order.get_time_left(user.cash)
            if time_next == 0:
                self._complete_order(order)
                return 0
            order.save()
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
        return time_next

    def _next(self, user, camera, session, extra_time, now):
        if extra_time is None:
            raise CameraAccessor.APIException("Need time")
        can_show, can_show_info = camera.can_show(user, now)
        if not can_show:
            if can_show_info == 'not_paid':
                time_left = camera.get_trial_view_time(session)
                if time_left > 0:
                    time_next = time_left - extra_time
                    camera.set_trial_view_time(session, time_next)
                    if time_next > 0:
                        if time_next > settings.TIME_INTERVAL_NOTIFY:
                            time_next = settings.TIME_INTERVAL_NOTIFY
                        return time_next
            return 0
        if can_show_info in ['owner', 'free']:
            return settings.TIME_INTERVAL_NOTIFY
        time_left, order = camera.get_show_info(user, now)
        if order.is_packet:
            time_next = self._check_packet(time_left)
        else:
            self._save_new_time(order, extra_time)
            time_next = order.get_time_left(user.cash)
            if time_next == 0:
                self._complete_order(order)
                return 0
            order.save()
            if time_next > settings.TIME_INTERVAL_NOTIFY:
                time_next = settings.TIME_INTERVAL_NOTIFY
        return time_next

    def _disconnect(self, user, camera, session, extra_time, now):
        if extra_time is None:
            raise CameraAccessor.APIException("Need time")
        can_show, can_show_info = camera.can_show(user, now)
        if not can_show:
            if can_show_info == 'not_paid':
                time_left = camera.get_trial_view_time(session)
                if time_left > 0:
                    time_next = time_left - extra_time
                    camera.set_trial_view_time(session, time_next)
            return 0
        if can_show_info in ['owner', 'free']:
            return 0
        time_left, order = camera.get_show_info(user, now)
        if order.is_packet:
            return 0
        self._save_new_time(order, extra_time)
        self._complete_order(order)
        return 0