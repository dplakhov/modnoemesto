from mongoengine.document import Document
from mongoengine.fields import StringField, ReferenceField, URLField, BooleanField, DateTimeField
from apps.utils.decorators import cached_property
from datetime import datetime
from mongoengine.queryset import OperationError


class GroupUser(Document):

    class STATUS:
        INVITE = 'invite'
        REQUEST = 'request'
        ACTIVE = 'active'

    group = ReferenceField('Group')
    user = ReferenceField('User', unique_with='group')
    is_admin = BooleanField(default=False)
    status = StringField(default=STATUS.ACTIVE)


class Group(Document):
    name = StringField(required=True, unique=True)
    description = StringField()
    theme = ReferenceField('GroupTheme')
    type = ReferenceField('GroupType')
    site = StringField()
    country = StringField()
    city = StringField()
    public = BooleanField(default=False)
    photo = ReferenceField('File')
    has_video_conference = BooleanField(default=True)

    @cached_property
    def members(self):
        return [i.user for i in GroupUser.objects(group=self, status=GroupUser.STATUS.ACTIVE).only('user')]

    def add_member(self, user, is_admin=False, status=GroupUser.STATUS.ACTIVE):
        try:
            GroupUser.objects.get_or_create(group=self,
                                            user=user,
                                            is_admin=is_admin,
                                            status=status)
        except OperationError:
            return False
        return True

    def is_active(self, user):
        return GroupUser.objects(group=self,
                                 user=user,
                                 status=GroupUser.STATUS.ACTIVE).count() > 0

    def is_request(self, user):
        return GroupUser.objects(group=self,
                                 user=user,
                                 status=GroupUser.STATUS.REQUEST).count() > 0

    def give_admin_right(self, user):
        info = GroupUser.objects(group=self,
                                 user=user,
                                 is_admin=False,
                                 status=GroupUser.STATUS.ACTIVE).first()
        if info:
            info.is_admin = True
            info.save()

    def remove_admin_right(self, user):
        info = GroupUser.objects(group=self,
                                 user=user,
                                 is_admin=True,
                                 status=GroupUser.STATUS.ACTIVE).first()
        if info:
            info.is_admin = False
            info.save()

    def can_remove_member(self, user):
        cnt = GroupUser.objects(group=self,
                                status=GroupUser.STATUS.ACTIVE,
                                is_admin=True).count()
        if cnt > 1:
            return True
        gu = GroupUser.objects(group=self, user=user).first()
        if not gu:
            return False
        return not gu.is_admin

    def remove_member(self, user):
        GroupUser.objects(group=self, user=user).delete()

    def is_admin(self, user):
        info = GroupUser.objects(group=self, user=user).only('is_admin').first()
        return info and info.is_admin


class GroupMessage(Document):
    group = ReferenceField('Group')
    sender = ReferenceField('User')
    text = StringField(required=True)
    timestamp = DateTimeField(default=datetime.now)

    meta = {
        'ordering': [
                '-timestamp',
        ]

    }


class GroupTheme(Document):
    name = StringField(required=True, unique=True)

    meta = {
        'ordering': [
            'name',
        ]
    }


class GroupType(Document):
    name = StringField(required=True, unique=True)

    meta = {
        'ordering': [
            'name',
        ]
    }