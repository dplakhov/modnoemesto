from mongoengine import *

from documents import User
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.shortcuts import redirect
from loginza import signals, models
from apps.social.documents import User
from apps.social.views import django_login
from django.contrib.auth import get_backends


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


def lazy_register(loginza_user, is_active=True):
    print "lazy_registering..."
    user = User(first_name=loginza_user.first_name,
                last_name=loginza_user.last_name,
                email=loginza_user.email,
                is_active=is_active,
                )
    user.save()
    profile = user.profile
    profile.mobile = ''
    profile.save()
    print "lazy_register", user
    return user


def loginza_auth_handler(sender, user, identity, **kwargs):
    redirect_to = sender.REQUEST.get(REDIRECT_FIELD_NAME, 'social:home')
    if not redirect_to or ' ' in redirect_to:
        redirect_to = settings.LOGIN_REDIRECT_URL
    elif '//' in redirect_to and re.match(r'[^\?]*//', redirect_to):
        redirect_to = settings.LOGIN_REDIRECT_URL
    try:
        # it's enough to have single identity verified to treat user as verified
        _user = models.UserMap.objects.get(user__username=user).user
        print _user
        mongo_user = None
        try:
            print "Mongodb User..."
            mongo_user = User.objects(email=user.email)[0]
            print "Mongodb User found"
        except:
            print "lazy_register start..."
            mongo_user = lazy_register(_user)
        print 123
        if mongo_user is not None:
            print "valid, signing in..."
            backend = get_backends()[0]
            mongo_user.backend = "%s.%s" % (backend.__module__, 
                                      backend.__class__.__name__)
            django_login(sender, mongo_user)
        else:
            print user, "is not valid"
    except Exception, e:#models.UserMap.DoesNotExist:
        print e
        sender.session['users_complete_reg_id'] = identity.id
    
    return redirect(redirect_to)

signals.authenticated.connect(loginza_auth_handler)



def get_user(userid):
    """Returns a User object from an id (User.id). Django's equivalent takes
    request, but taking an id instead leaves it up to the developer to store
    the id in any way they want (session, signed cookie, etc.)
    """
    if not userid:
        return AnonymousUser()
    return MongoEngineBackend().get_user(userid) or AnonymousUser()
