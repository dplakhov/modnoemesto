from apps.news.documents import News


class LastNewsMiddleware:
    def process_request(self, request):
        request.last_news = News.objects.first()