from django.test import TestCase

from apps.news.tasks import send_notification
from apps.news.documents import News
from apps.social.documents import User

class AddTestCase(TestCase):
    def setUp(self):
        self.acc1 = User.create_user(email='eugene@web-mark.ru', password='123')
        self.news_object = News(
            title="test news title",
            text="test news text",
            preview_text="test news preview text",
            author=self.acc1 
        )
        self.news_object.save()

    def tearDown(self):
        User.objects.delete()
        News.objects.delete()
        
        
    def testNoError(self):
        result = send_notification.delay(self.news_object.id)
        #print "result.status=", result.status
        #print "result.traceback=", result.traceback
        
        self.assertTrue(result.successful())