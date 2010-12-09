from mongoengine import *

from documents import User
from django.contrib.auth.models import AnonymousUser

class MongoEngineBackend(object):
    """Authenticate using MongoEngine and mongoengine.django.auth.User.
    """

    def authenticate(self, email=None, password=None):
        user = User.objects(email=email).first()
        if user:
            if password and user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        #@todo: need merge User and User
        from .documents import User
        return User.objects.with_id(user_id)


def get_user(userid):
    """Returns a User object from an id (User.id). Django's equivalent takes
    request, but taking an id instead leaves it up to the developer to store
    the id in any way they want (session, signed cookie, etc.)
    """
    if not userid:
        return AnonymousUser()
    return MongoEngineBackend().get_user(userid) or AnonymousUser()
