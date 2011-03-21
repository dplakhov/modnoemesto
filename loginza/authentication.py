# -*- coding:utf-8 -*-
from apps.social.documents import User

class LoginzaBackend(object):
    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, user_map=None):
        return user_map.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Exception,e:
            print e
            return None


class LoginzaError(object):
    type = None
    message = None

    def __init__(self, data):
        self.type = data['error_type']
        self.message = data['error_message']
