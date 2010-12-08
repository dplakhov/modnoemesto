from datetime import datetime
from apps.social.documents import User


class SetLastAccessMiddleware:
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.last_access = datetime.now()
            User.objects(id=request.user.id).update_one(set__last_access=request.user.last_access)