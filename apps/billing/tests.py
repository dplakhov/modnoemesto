import urllib
import urlparse
from apps.billing.documents import AccessCamOrder, Tariff
from apps.cam.documents import Camera, CameraType
from django.core.urlresolvers import reverse
from apps.billing.models import UserOrder
from django.conf import settings
from django.test.client import Client
from apps.billing.constans import TRANS_STATUS
from apps.social.documents import User
import unittest
import time


class AcessCameraTest(unittest.TestCase):

    def setUp(self):
        self.tearDown()

        self.client = Client()

        self.camera_type_axis = CameraType(
            name='Axis',
            driver='axis.AxisDriver',
            is_controlled=False,
        )
        self.camera_type_axis.save()
        self.camera_type_axis_manage = CameraType(
            name='Axis Manage',
            driver='axis.AxisDriver',
            is_controlled=True,
        )
        self.camera_type_axis_manage.save()

        self.tariff_view_package = Tariff(
            name='View Package 1 min',
            description='View Package Description...',
            cost=1.0,
            duration=2,
            is_controlled=False,
        )
        self.tariff_view_package.save()

        self.tariff_view_time = Tariff(
            name='View Package Time',
            description='View Package Description...',
            cost=1.0,
            is_controlled=False,
        )
        self.tariff_view_time.save()

        self.tariff_manage_package = Tariff(
            name='Manage Package 1 min',
            description='Manage Package Description...',
            cost=2.0,
            duration=2,
            is_controlled=True,
        )
        self.tariff_manage_package.save()

        self.tariff_manage_time = Tariff(
            name='Manage Package Time',
            description='Manage Package Description...',
            cost=2.0,
            is_controlled=True,
        )
        self.tariff_manage_time.save()

        for i in xrange(1, 4):
            user = User.create_user(email='test%i@web-mark.ru' % i, password='123')
            user.cash = 1000000.0
            user.save()
            camera = Camera(
                name='Test Billing Camera %i' % i,
                owner=user,
                type=self.camera_type_axis_manage,
                stream_name='boston',
                camera_management_host='localhost.boston.com',
                camera_management_username='test',
                camera_management_password='321',
                is_view_enabled=True,
                is_view_public=True,
                is_view_paid=True,
                is_management_enabled=True,
                is_management_public=True,
                is_management_paid=True,
                is_managed=True,
                management_packet_tariff=self.tariff_manage_package,
                management_time_tariff=self.tariff_manage_time,
                view_packet_tariff=self.tariff_view_package,
                view_time_tariff=self.tariff_view_time,
            )
            camera.save()

    def tearDown(self):
        CameraType.objects.delete()
        Tariff.objects.delete()
        Camera.objects.delete()
        AccessCamOrder.objects.delete()
        User.objects.delete()

    def test_access_view_package(self):
        def get_access():
            user = User.objects.get(email='test1@web-mark.ru')
            camera = Camera.objects.get(name='Test Billing Camera 2')
            return AccessCamOrder.create_packet_type(
                tariff=self.tariff_view_package,
                count_packets=1,
                user=user,
                camera=camera,
            )

        order = get_access()

        self.assertEqual(order.can_access(), True)
        time.sleep(1)
        self.assertEqual(order.can_access(), True)
        time.sleep(1)
        self.assertEqual(order.can_access(), False)

        get_access() # 2 sec
        get_access() # 4 sec
        get_access() # 6 sec

        camera = Camera.objects.get(name='Test Billing Camera 2')
        user_payed = User.objects.get(email='test1@web-mark.ru')
        user_owner = User.objects.get(email='test2@web-mark.ru')
        user_other = User.objects.get(email='test3@web-mark.ru')

        self.assertEqual(camera.billing(camera.owner, user_payed)['can_show'], True)
        self.assertEqual(camera.billing(camera.owner, user_owner)['can_show'], False)
        self.assertEqual(camera.billing(camera.owner, user_other)['can_show'], False)
        time.sleep(4)
        self.assertEqual(camera.billing(camera.owner, user_payed)['can_show'], True)
        self.assertEqual(camera.billing(camera.owner, user_owner)['can_show'], False)
        self.assertEqual(camera.billing(camera.owner, user_other)['can_show'], False)
        time.sleep(4)
        self.assertEqual(camera.billing(camera.owner, user_payed)['can_show'], False)
        self.assertEqual(camera.billing(camera.owner, user_owner)['can_show'], False)
        self.assertEqual(camera.billing(camera.owner, user_other)['can_show'], False)

    def test_access_view_time(self):
        def get_access():
            user = User.objects.get(email='test1@web-mark.ru')
            camera = Camera.objects.get(name='Test Billing Camera 2')
            return AccessCamOrder.create_time_type(
                tariff=self.tariff_view_time,
                user=user,
                camera=camera,
            )

        def view_notify(camera_id, status='view'):
            params = dict(
                status=status,
                session_key=self.client.session.session_key,
                camera_id=camera_id,
                time=settings.TIME_INTERVAL_NOTIFY,
            )
            response = self.client.get('%s?%s' % (reverse('server_api:cam_view_notify'), urllib.urlencode(params)))
            answer = dict(urlparse.parse_qsl(response.content))
            self.assertEqual(answer['info'], 'OK')


        self.client.login(email='test1@web-mark.ru', password='123')

        order = get_access()

        try:
            bad_order = get_access()
        except AccessCamOrder.CanNotAddOrder:
            bad_order = None
        self.assertEqual(bad_order, None)

        order = AccessCamOrder.objects.get(id=order.id)
        self.assertEqual(order.can_access(), True)
        time.sleep(settings.TIME_INTERVAL_NOTIFY)
        view_notify(order.camera.id)
        order = AccessCamOrder.objects.get(id=order.id)
        self.assertEqual(order.can_access(), True)
        time.sleep(settings.TIME_INTERVAL_NOTIFY)
        view_notify(order.camera.id, 'disconnect')
        order = AccessCamOrder.objects.get(id=order.id)
        self.assertEqual(order.can_access(), False)


class BillingTest(unittest.TestCase):

    def setUp(self):
        self.cleanUp()
        self.c = Client()
        self.user = User.create_user(email='test@web-mark.ru', password='123')
        self.base_url = reverse('operator')
        self.auth_dict = {
            'duser': settings.PKSPB_DUSER,
            'dpass': settings.PKSPB_DPASS,
            'cid': self.user.id,
            'sid': '1',
        }
        self.TRANS_COUNT = 100

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        UserOrder.objects.all().delete()
        User.objects.delete()

    def test_operator_get_info(self):
        data = self.auth_dict.copy()
        data.update({
            'uact': 'get_info',
        })
        response = self.c.get(self.base_url, data=data)
        self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.SUCCESSFUL)

    def test_operator_bad_sid(self):
        for i in ['2', '-1', '2r3', 'yy', '1.0', '']:
            data = self.auth_dict.copy()
            data.update({
                'uact': 'get_info',
                'sid': i,
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def test_operator_bad_term(self):
        for i in ['-2', '2r3', 'yy', '1.0', '']:
            data = self.auth_dict.copy()
            data.update({
                'uact': 'payment',
                'term': i,
                'trans': 1,
                'sum': "1.00",
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def test_operator_bad_trans(self):
        for i in ['-2', '2r3', 'yy', '1.0', '']:
            data = self.auth_dict.copy()
            data.update({
                'uact': 'payment',
                'term': i,
                'trans': 1,
                'sum': "1.00",
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def test_operator_bad_sum(self):
        for i in ['-2', '2r3', 'yy', '-2.00', '']:
            data = self.auth_dict.copy()
            data.update({
                'uact': 'payment',
                'term': 1,
                'trans': 1,
                'sum': i,
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.INVALID_PARAMS)

    def test_operator_add_payments(self):
        for i in xrange(1, self.TRANS_COUNT+1):
            data = self.auth_dict.copy()
            sum = "%i.00" % i
            data.update({
                'uact': 'payment',
                'term': i,
                'trans': i,
                'sum': sum,
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i&summa=%s' % (TRANS_STATUS.SUCCESSFUL, sum))
        for i in xrange(1, self.TRANS_COUNT+1):
            data = self.auth_dict.copy()
            sum = "%i.00" % i
            data.update({
                'uact': 'payment',
                'term': i,
                'trans': i,
                'sum': sum,
            })
            response = self.c.get(self.base_url, data=data)
            self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.ALREADY)
        count = UserOrder.objects.count()
        self.assertEqual(count, self.TRANS_COUNT)

    def test_operator_view_order_list(self):
        response = self.c.get(reverse('billing:order_list'))
        self.assertEqual(response.status_code, 302)

        response = self.c.get("%s?page=2" % reverse('billing:order_list'))
        self.assertEqual(response.status_code, 302)