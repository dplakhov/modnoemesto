from apps.social.documents import User
from django.db import models
from django.utils import simplejson as json
from mongoengine.fields import ReferenceField, StringField, BooleanField
from mongoengine.document import Document

from apps.loginza import signals
from apps.loginza.conf import settings

def from_loginza_data(loginza_data):
    try:
        identity = Identity.objects.get(identity=loginza_data['identity'])
        # update data as some apps can use it, e.g. avatars
        identity.data=json.dumps(loginza_data)
        identity.save()
    except Exception,e:
        identity = Identity(
                identity=loginza_data['identity'],
                provider=loginza_data['provider'],
                data=json.dumps(loginza_data)
                )
        identity.save()
    return identity


def for_identity(identity, request):
    try:
        user_map = UserMap.objects.get(identity=identity)
    except:
        # if there is authenticated user - map identity to that user
        # if not - create new user and mapping for him
        if request.user.is_authenticated():
            user = request.user
        else:
            loginza_data = json.loads(identity.data)

            loginza_email = loginza_data.get('email', '')
            try:
                loginza_data['first_name'] = loginza_data['name']['first_name']
                loginza_data['last_name'] = loginza_data['name']['last_name']
            except:
                pass
                
            email = loginza_email if '@' in loginza_email else settings.DEFAULT_EMAIL

            # if nickname is not set - try to get it from email
            # e.g. vgarvardt@gmail.com -> vgarvardt
            loginza_nickname = loginza_data.get('nickname', None)
            username = loginza_nickname if loginza_nickname is not None else email.split('@')[0]
            if 'uid' in loginza_data:
                username = str(loginza_data['uid'])

            try:
                user = User.objects.get(email=email)
            except Exception,e:
                user = User(username=username, email=email)
                user.save()
        user_map = UserMap(identity=identity, user=user)
        signals.created.send(request, user_map=user_map)
    return user_map


class Identity(Document):
    identity = StringField(unique=True)
    provider = StringField()
    data = StringField()

    def __unicode__(self):
        return self.identity

    class Meta:
        ordering = ['id']
        verbose_name_plural = "identities"


class UserMap(Document):
    identity = ReferenceField('Identity')
    user = ReferenceField('User')
    verified = BooleanField(default=False)

    def __unicode__(self):
        return '%s [%s]' % (unicode(self.user), self.identity.provider)

    class Meta:
        ordering = ['user']
