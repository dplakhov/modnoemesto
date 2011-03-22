from apps.social.documents import User
from django.db import models
from django.utils import simplejson as json
from mongoengine.fields import ReferenceField, StringField, BooleanField
from mongoengine.document import Document

from loginza import signals
from loginza.conf import settings

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
    """
    uid: google,vkontakte,facebook,twitter,loginza,lastffm,
    language: google,flickr, yahoo
    email: google, yandex,facebook,loginza,flickr, yahoo
    name 
        first_name: google,vkontakte,facebook,loginza,
        last_name: google,vkontakte,facebook,loginza,
        full_name: google, yandex,facebook,twitter,loginza,flickr, yahoo, lastffm,
    dob: yandex,vkontakte,facebook,loginza,
    nickname: yandex,vkontakte,twitter,loginza,flickr, yahoo, lastffm,
    photo: vkontakte, facebook,twitter,loginza,flickr, yahoo, lastffm,
    gender: vkontakte,facebook,loginza,flickr, yahoo, lastffm,
    address
        home
            country: vkontakte, lastffm,
    web: twitter
        default: lastffm,
    biography: twitter,
    """
    try:
        user_map = UserMap.objects.get(identity=identity)
    except:
        # if there is authenticated user - map identity to that user
        # if not - create new user and mapping for him
        if request.user.is_authenticated():
            user = request.user
        else:
            loginza_data = json.loads(identity.data)
            loginza_name_dict = dict(first_name='', last_name='', full_name='')
            loginza_home_dict = dict(country='')
            loginza_address_dict = dict(home=loginza_home_dict)

            loginza_email = loginza_data.get('email', '')
            loginza_uid = loginza_data.get('uid', '')
            loginza_language = loginza_data.get('language', '')
            loginza_first_name = loginza_data.get('name', loginza_name_dict)\
                                             .get('first_name','')
            loginza_last_name = loginza_data.get('name', loginza_name_dict)\
                                            .get('last_name','')
            loginza_full_name = loginza_data.get('name', loginza_name_dict)\
                                            .get('full_name','')
            if not loginza_first_name and not loginza_last_name \
            and loginza_full_name:
                loginza_first_name = loginza_full_name
            loginza_dob = loginza_data.get('dob', '')
            loginza_nickname = loginza_data.get('nickname', '')
            loginza_photo = loginza_data.get('photo', '')
            loginza_gender = loginza_data.get('gender', '')
            loginza_country = loginza_data.get('address', loginza_address_dict)\
                                          .get('home', loginza_home_dict)\
                                          .get('country', '')
            loginza_web = loginza_data.get('web', '')
            if isinstance(loginza_web, dict):
                loginza_web = loginza_web.get('default', '')
            loginza_bio = loginza_data.get('biography', '')

            email = loginza_email if '@' in loginza_email else settings.DEFAULT_EMAIL

            if loginza_email:
                username = loginza_email
            elif loginza_nickname:
                username = loginza_nickname
            elif 'uid' in loginza_data:
                username = str(loginza_data['uid'])
            else:
                username = loginza_data['identity']

            # if nickname is not set - try to get it from email
            # e.g. vgarvardt@gmail.com -> vgarvardt
            loginza_nickname = loginza_data.get('nickname', None)
            username = loginza_nickname if loginza_nickname is not None else email.split('@')[0]
            if 'uid' in loginza_data:
                username = str(loginza_data['uid'])

            
            try:
                user = User.objects.get(username=username)
            except Exception,e:
                try:    
                    user = User.objects.get(email=email)
                except:
                    user = User(username=username, email=email, 
                                first_name=loginza_first_name, 
                                last_name=loginza_last_name)
                    user.save()
                    profile = user.profile
                    if loginza_dob:
                        profile.birthday = loginza_dob
                    if loginza_gender:
                        profile.sex = loginza_gender
                    if loginza_web:
                        profile.website = loginza_web
                    if loginza_dob or loginza_gender or loginza_web:
                        profile.save()
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
