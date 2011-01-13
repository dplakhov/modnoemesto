from datetime import datetime, timedelta
from django.conf import settings
from apps.social.documents import User



class SetLastAccessMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated():
            now = datetime.now()
            if now - request.user.last_access > settings.LAST_ACCESS_UPDATE_INTERVAL:
                request.user.last_access = now
                User.objects(id=request.user.id).update_one(set__last_access=now)