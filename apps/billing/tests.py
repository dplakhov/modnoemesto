from django.core.urlresolvers import reverse
from apps.billing.models import UserOrder
from django.conf import settings
from django.test.client import Client
from apps.billing.constans import TRANS_STATUS
import unittest
from apps.social.documents import User


class BillingTest(unittest.TestCase):

    def setUp(self):
        self.cleanUp()
        self.c = Client()
        self.user = User.create_user(username='test', password='123')
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

        response = self.c.get(reverse('billing:order_list_page', args=[2]))
        self.assertEqual(response.status_code, 302)