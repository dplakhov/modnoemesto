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
        self.c.login(username='test', password='123')

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        User.objects.delete()

    def test_pay_operator(self):
        base_url = reverse('operator')

        response = self.c.get(base_url)
        self.assertEqual(response.status_code, 200)

        order = UserOrder(user=self.user)
        order.save()

        auth_dict = {
            'duser': settings.PKSPB_DUSER,
            'dpass': settings.PKSPB_DPASS,
            'cid': order.id,
            'sid': '1',
        }

        data = auth_dict.copy()
        data.update({
            'uact': 'get_info',
        })
        response = self.c.get(base_url, data=data)
        self.assertEqual(response.content, 'status=%i' % TRANS_STATUS.SUCCESSFUL)

        TERM = '1'
        TRANS = '1'
        SUM = '1.00'

        auth_dict = auth_dict.copy()
        auth_dict.update({
            'term': TERM,
            'trans': TRANS,
            'sum': SUM,
        })

        data = auth_dict.copy()
        data.update({
            'uact': 'prepayment',
        })
        response = self.c.get(base_url, data=data)
        self.assertEqual(response.content, 'status=%i&summa=%s' % (TRANS_STATUS.SUCCESSFUL, SUM))

        data = auth_dict.copy()
        data.update({
            'uact': 'payment',
        })
        response = self.c.get(base_url, data=data)
        self.assertEqual(response.content, 'status=%i&summa=%s' % (TRANS_STATUS.SUCCESSFUL, SUM))