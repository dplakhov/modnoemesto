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

    def tearDown(self):
        self.cleanUp()

    def cleanUp(self):
        UserOrder.objects.all().delete()
        User.objects.delete()

    def test_pay_operator(self):
        base_url = reverse('operator')

        response = self.c.get(base_url)
        self.assertEqual(response.status_code, 200)

        auth_dict = {
            'duser': settings.PKSPB_DUSER,
            'dpass': settings.PKSPB_DPASS,
            'cid': self.user.id,
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
        SUM = '10.00'

        data = auth_dict.copy()
        data.update({
            'uact': 'payment',
            'term': TERM,
            'trans': TRANS,
            'sum': SUM,
        })
        response = self.c.get(base_url, data=data)
        self.assertEqual(response.content, 'status=%i&summa=%s' % (TRANS_STATUS.SUCCESSFUL, SUM))

        count = UserOrder.objects.filter(user=self.user, trans=TRANS).count()
        self.assertEqual(count, 1)
